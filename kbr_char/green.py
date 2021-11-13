import ast
import json
import operator
from loguru import logger
from _ast import Constant, operator as op_type
from typing import Any, Mapping, Optional, Sequence, Union
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
    component_type: str
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
        self.components = []
        for ctype, component_list in self.init_data.items():
            for component in component_list:
                self.components.append(SpellComponent(ctype, **component))

    def get_component(self, name: str) -> SpellComponent:
        filtered_components = [com for com in self.components if com.name == name]
        return filtered_components[0]


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
