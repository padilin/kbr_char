from __future__ import annotations
import json
import ast
import operator
import os.path
import pickle
from _ast import Constant
from dataclasses import dataclass, field
from typing import Type, Any, List
from pprint import pprint as print


_OP_MAP = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Invert: operator.neg,
    ast.Pow: operator.pow,
}


class Calc(ast.NodeVisitor):
    """See https://github.com/benreu/PyGtk-Posting/commit/9a34641b62c9639599641f9965ef5ffbb752cb3a"""

    def visit_BinOp(self, node):
        left = self.visit(node.left)
        right = self.visit(node.right)
        return _OP_MAP[type(node.op)](left, right)

    def visit_Constant(self, node: Constant) -> Any:
        return node.n

    def visit_Expr(self, node):
        return self.visit(node.value)

    @classmethod
    def evaluate(cls, expression):
        tree = ast.parse(expression)
        calc = cls()
        return calc.visit(tree.body[0])


@dataclass()
class Quality:
    """
    Class that holds the data for the different spell qualities.
    :param str name: Name of quality
    :param int x: Numeric value of quality
    :param str spell_name: Name of attached spell
    :param str desc: Part that gets built into spell description
    :param str catagory: Overarching catagory this belongs to
    :param str sub: Sub-type of element
    :param str units: Units of value, ex: ft, mi, in
    :param str formula: Representation of formula, value substitute for x
    """
    # required
    name: str
    x: int

    # meta
    spell_name: str = None
    _formula: str = None

    # optional
    desc: str = None
    catagory: str = None
    sub: str = None
    units: str = None
    formula: str = "x" # Formula defaults to passing in value to x, to allow easy defining no formula qualities

    @property
    def dc(self) -> int:
        """
        :return: Return difficulty of quality.
        :rtype: int
        """
        if self.formula:
            self._formula = self.formula.replace("x", str(self.x))
            return int(Calc.evaluate(self._formula))
        else:
            return self.x

    def __repr__(self):
        return self.desc

    def __str__(self):
        return self.__repr__()


@dataclass
class Spell:
    """
    Class that holds a single spell and all of its attributes.
    :param str name: Name of spell
    :param qualities: A list of qualities
    :type: list(Quality)
    """
    name: str
    qualities: list[Quality] = field(default_factory=list)

    _dc: int = 0
    _desc: str = None
    _order: list[str] = field(default_factory=list)

    @property
    def dc(self) -> int:
        """
        :return: Return difficulty of spell.
        :rtype: int
        """
        self._dc = 0
        for quality in self.qualities:
            self._dc += quality.dc
        return self._dc

    def add_quality(self, quality: Quality, value: int = None) -> None:
        """
        :param quality: Takes a quality, processes it, adds it to self.
        :type: Quality
        :param value: Takes in the numeric value, 'x', of a quality.
        :type: int
        """
        _quality = quality
        if value:
            _quality.x = value
        self.qualities.append(_quality)

    def process_desc(self) -> str:
        _desc = ""
        elements_qualities = self.get_qualities(category="Elements")
        range_qualities = self.get_qualities(category="Range")
        shape_qualities = self.get_qualities(category="Shape")
        modifiers_qualities = self.get_qualities(category="Modifiers")
        misc_qualities = list()
        misc_categories = list([x for x in self._order if x not in ["Elements", "Range", "Shape", "Modifiers"]])
        _desc = self.name.title() + " with a dc of " + str(self.dc) + " : " + " and ".join(self._return_desc(elements_qualities)) + " is a " + " and ".join(self._return_desc(range_qualities)) + " spell that is a " + " and ".join(self._return_desc(shape_qualities))
        if modifiers_qualities:
            _desc = _desc + " that " + " and ".join(self._return_desc(modifiers_qualities))
        if misc_qualities:
            _desc = _desc + " " + " and ".join(self._return_desc(misc_qualities))
        self._desc = _desc
        return self._desc

    def _return_desc(self, qualities: list[Quality]) -> list[str]:
        result = list()
        for item in qualities:
            _desc = item.desc
            if item.units:
                _desc = _desc + " of " + str(item.x) + " " + item.units
            result.append(_desc)
        return result

    def get_qualities(self, name: str = None, category: str = None) -> list[Quality]:
        if name:
            return list([x for x in self.qualities if x.name == name])
        elif category:
            return list([x for x in self.qualities if x.catagory == category])
        else:
            return self.qualities

    def __repr__(self):
        return self.process_desc()

    def __str__(self):
        return self.__repr__()


@dataclass
class SpellFactory:
    quality_config: dict[str, str] | str = field(default_factory=dict)
    spells: list[Spell] =  field(default_factory=list)
    order: list[str] = field(default_factory=list)

    def __post_init__(self):
        self.qualities = self.load_qualities(self.quality_config)

    def save(self, filename: str) -> None:
        with open(filename, "wb") as f:
            pickle.dump(self.__dict__, f)

    @classmethod
    def load(cls, filename: str):
        with open(filename, "rb") as f:
            attribs = pickle.load(f)
            result = SpellFactory()
            result.__dict__ = attribs
            return result

    def __repr__(self) -> str:
        return f"Codex (Qualities: {len(self.qualities)}, Spells: {len(self.spells)})"

    def __str__(self) -> str:
        return self.__repr__()

    def __getattr__(self, item) -> Quality:  # Change this to look through self.quality_config so i can pass that dict to class Spell to make and add quality
        for quality in self.qualities:
            if quality.name == item:
                return quality
        else:
            raise AttributeError

    def load_qualities(self, _json: str) -> List[Quality]: # Move up to class Spell, take dict from SpellFactory.quality_config and make Quality list on class Spell for modifying x value
        results = list()
        if isinstance(_json, str):
            data = json.loads(_json)
        if isinstance(_json, dict):
            data = _json
        for k, v in data.items():
            self.order.append(k)
            for quality in v:
                results.append(Quality(**quality, catagory=k))
        return results

    def create_spell(self, name: str) -> Spell:
        spell = Spell(name)
        spell._order = self.order
        self.spells.append(spell)
        return spell


if __name__ == "__main__":
    print("Testing loading spells from json")
    test_1 = None
    with open('kbr_char/spells.json', 'r') as f:
        test_1 = json.load(f)
    Codex = SpellFactory(test_1)
    print(f"Loaded json: {Codex=}")

    print("Testing Save, filename is 'codex_test'")
    filename = "codex_test"
    Codex.save(filename)
    print("Save complete")
    if os.path.isfile(filename):
        print(f"{filename} is a file")
    else:
        print(f"{filename} is not a file!")

    print(f"Testing loading from {filename}")
    Codex2 = SpellFactory.load(filename)
    print(f"Sucessfully loaded {Codex2=}")

    Fireball = Codex2.create_spell("fireball")
    print("combustion")
    Fireball.add_quality(Codex2.Combustion)
    print("blast")
    Fireball.add_quality(Codex2.Blast)
    print("range")
    Fireball.add_quality(Codex2.SpellRange, 100)
    print("arrow")
    Fireball.add_quality(Codex2.Arrow)
    print("effect distance")
    Fireball.add_quality(Codex2.EffectDistance, 20)
    print(f"{Fireball=}")
    print(f"{Fireball.name} with a dc of {Fireball.dc}")

    print(Fireball.get_qualities(category="Elements"))
