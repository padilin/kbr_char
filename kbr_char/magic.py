from __future__ import annotations  # For using | with type hints

import ast
import json
import operator
from _ast import Constant
from _ast import operator as op_type
from dataclasses import dataclass, field
from typing import Any, Optional, Type

from loguru import logger


class Calc(ast.NodeVisitor):
    """See https://github.com/benreu/PyGtk-Posting/commit/9a34641b62c9639599641f9965ef5ffbb752cb3a"""

    @staticmethod
    def translate_op(op: op_type):
        op_map = {
            ast.Add: operator.add,
            ast.Sub: operator.sub,
            ast.Mult: operator.mul,
            ast.Div: operator.truediv,
            ast.Invert: operator.neg,
            ast.Pow: operator.pow,
        }
        return op_map[type(op)]

    def visit_BinOp(self, node):
        left = self.visit(node.left)
        right = self.visit(node.right)
        return self.translate_op(node.op)(left, right)

    def visit_Constant(self, node: Constant) -> Any:
        return node.n

    def visit_Expr(self, node):
        return self.visit(node.value)

    @classmethod
    def evaluate(cls, expression):
        tree = ast.parse(expression)
        calc = cls()
        return calc.visit(tree.body[0])


@dataclass
class SpellComponent:
    name: str
    x: int
    formula: str
    units: Optional[str] = None
    desc: Optional[str] = None

    @property
    def dc(self) -> int:
        formulae = self.formula.replace("x", str(self.x))
        return int(Calc.evaluate(formulae))

    def customize(self, x: int):
        self.x = x

    def __str__(self):
        return self.name


class Element(SpellComponent):
    ...


class Range(SpellComponent):
    ...


class Shape(SpellComponent):
    ...


class Modifier(SpellComponent):
    ...


def load_data(filepath: str) -> dict:

    with open(filepath) as file_object:
        file_content = file_object.read()

    config_data = json.loads(file_content)

    return config_data


@dataclass
class SpellComponentCollection:
    # Remember that order will determine arg input. Keep init_data 1st.
    init_data: dict[str, list[dict[str, str | int]]] = field(default_factory=dict)
    components: list[SpellComponent] = field(default_factory=list)

    def __post_init__(self) -> None:
        elements: list[Element] = [Element(**x) for x in self.init_data["Elements"]]
        ranges: list[Range] = [Range(**x) for x in self.init_data["Range"]]
        shapes: list[Shape] = [Shape(**x) for x in self.init_data["Shape"]]
        modifiers: list[Modifier] = [Modifier(**x) for x in self.init_data["Modifiers"]]

        for (
            item_elem
        ) in (
            elements
        ):  # TODO: Find a better way. Typing changes after first item is appended...
            self.components.append(item_elem)
        for item_range in ranges:
            self.components.append(item_range)
        for item_shape in shapes:
            self.components.append(item_shape)
        for item_mod in modifiers:
            self.components.append(item_mod)

    def get(self, component_type: Type[SpellComponent], name: str) -> SpellComponent:
        filtered = [
            x
            for x in self.components
            if isinstance(x, component_type) and x.name.lower() == name.lower()
        ]
        return filtered[0]

    def get_by_type(self, component_type: Type[SpellComponent]) -> list[SpellComponent]:
        filtered = [x for x in self.components if isinstance(x, component_type)]
        return filtered

    def get_by_name(self, name: str) -> list[SpellComponent]:
        filtered = [x for x in self.components if x.name.lower() == name.lower()]
        return filtered


@dataclass
class Spell:
    name: str
    components: list[SpellComponent] = field(default_factory=list)

    def add_component(self, component: SpellComponent) -> None:
        self.components.append(component)

    @property
    def dc(self):
        return sum([x.dc for x in self.components])


@dataclass
class SpellBook:
    name: str
    spells: list[Spell] = field(default_factory=list)
    components: Optional[SpellComponentCollection] = None

    def spell_list(self) -> list[str]:
        return [spell.name for spell in self.spells]

    def detailed_spell_list(self) -> list[Spell]:
        return self.spells

    def add_spell(self, spell: Spell) -> None:
        if spell.name in self.spell_list():
            raise ValueError(f"Spell already in SpellBook {self.name}")
        self.spells.append(spell)

    def remove_spell(self, spellname: str) -> None:
        filtered = [
            spell_index
            for spell_index, spell in enumerate(self.spells)
            if spell.name == spellname
        ]
        if filtered and len(filtered) == 1:
            self.spells.pop(filtered[0])

    def get_spell(self, spellname: str) -> Spell:
        filtered = [spell for spell in self.spells if spell.name == spellname]
        return filtered[0]

    def load_components(self, data: dict[str, list[dict[str, str | int]]]):
        self.components = SpellComponentCollection(data)


if __name__ == "__main__":
    # Usage example

    # Data setup
    test_data_load = load_data("magic.json")
    MySpellBook = SpellBook("My Spell Book")
    MySpellBook.load_components(test_data_load)

    # Spell Construction
    fireball = Spell("Fireball")

    spell_element = MySpellBook.components.get(Element, "Combustion")
    spell_range = MySpellBook.components.get(Range, "SpellRange")
    spell_shape = MySpellBook.components.get(Shape, "Arrow")

    spell_range.customize(100)  # Change range to 100 ft

    fireball.add_component(spell_element)
    fireball.add_component(spell_range)
    fireball.add_component(spell_shape)

    # SpellBook Construction
    MySpellBook.add_spell(fireball)

    # Demo Output
    logger.debug(f"Spells in {MySpellBook}: {MySpellBook.spell_list()}")
    logger.debug(f"Spell: {MySpellBook.get_spell('Fireball')}")
    logger.debug(f"Spell Name: {MySpellBook.get_spell('Fireball').name}")
    logger.debug(f"Spell DC: {MySpellBook.get_spell('Fireball').dc}")

    # To test this code out, run: pytest tests/test_magic.py
