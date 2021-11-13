import ast
import json
import operator
from loguru import logger
from _ast import Constant, operator as op_type
from typing import Any, Mapping, Optional, Sequence
from dataclasses import dataclass, field


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


class Element(SpellComponent):
    ...


class Range(SpellComponent):
    ...


class Shape(SpellComponent):
    ...


class Modifier(SpellComponent):
    ...


def load_data(filepath: str) -> Mapping:

    with open(filepath) as file_object:
        file_content = file_object.read()

    config_data = json.loads(file_content)

    return config_data


@dataclass
class SpellComponentCollection:
    # Remember that order will determine arg input. Keep init_data 1st.
    init_data: Mapping = field(default_factory=dict)

    def __post_init__(self) -> None:
        self.elements = [Element(**x) for x in self.init_data["Elements"]]
        self.ranges = [Range(**x) for x in self.init_data["Range"]]
        self.shapes = [Shape(**x) for x in self.init_data["Shape"]]
        self.modifiers = [Modifier(**x) for x in self.init_data["Modifiers"]]

    def get_element(self, name: str) -> Element:
        filtered_elements = [e for e in self.elements if e.name == name]
        return filtered_elements[0]
    
    def get_range(self, name: str) -> Range:
        filtered_elements = [r for r in self.ranges if r.name == name]
        return filtered_elements[0]
    
    def get_shape(self, name: str) -> Shape:
        filtered_elements = [s for s in self.shapes if s.name == name]
        return filtered_elements[0]
    
    def get_modifier(self, name: str) -> Modifier:
        filtered_elements = [m for m in self.modifiers if m.name == name]
        return filtered_elements[0]


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


# if __name__ == "__main__":
#     # Usage example

#     # Data setup
#     test_data_load = load_data("kbr_char/green.json")
#     spell_components = SpellComponentCollection(test_data_load)
#     logger.info(spell_components)

#     # Spell Construction
#     fireball = Spell("Fireball")

#     spell_element = spell_components.get_element("Combustion")
#     spell_range = spell_components.get_range("SpellRange")
#     spell_shape = spell_components.get_shape("Arrow")

#     spell_range.customize(100)  # Change range to 100 ft

#     fireball.add_component(spell_element)
#     fireball.add_component(spell_range)
#     fireball.add_component(spell_shape)

#     # SpellBook Construction
#     my_spellbook = SpellBook("Exodius")
#     my_spellbook.add_spell(fireball)

#     # Demo Output
#     logger.debug(my_spellbook.spell_list())
#     logger.debug(my_spellbook.get_spell("Fireball"))
#     logger.debug(my_spellbook.get_spell("Fireball").name)
#     logger.debug(my_spellbook.get_spell("Fireball").dc)

#     # To test this code out, run: pytest tests/test_green.py
