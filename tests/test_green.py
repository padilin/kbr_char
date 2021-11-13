import operator

import pytest
from kbr_char.green import (
    load_data,
    SpellComponentCollection,
    Spell,
    SpellBook,
    Calc,
)


class TestSpellComponentCollections:
    @classmethod
    def setup_class(cls):
        test_data = load_data("kbr_char/green.json")
        cls.spell_components = SpellComponentCollection(test_data)

    def test_retrieving_an_element(self):
        spell_component = self.spell_components.get_element("Combustion")
        assert spell_component.name == "Combustion"

    def test_retrieving_a_range(self):
        spell_component = self.spell_components.get_range("SpellRangeTouch")
        assert spell_component.name == "SpellRangeTouch"

    def test_retrieving_a_shape(self):
        spell_component = self.spell_components.get_shape("Arrow")
        assert spell_component.name == "Arrow"

    def test_retrieving_a_modifier(self):
        spell_component = self.spell_components.get_modifier("RangeDistance")
        assert spell_component.name == "RangeDistance"

    def test_exception_when_retrieving_a_nonexistant_component_name(self):
        with pytest.raises(IndexError):
            self.spell_components.get_element("NonExistant")

    def test_customizing_component(self):
        spell_component = self.spell_components.get_range("SpellRange")
        spell_component.customize(100)
        assert spell_component.dc == 60


class TestSpell:
    @classmethod
    def setup_class(cls):
        test_data = load_data("kbr_char/green.json")
        cls.spell_components = SpellComponentCollection(test_data)

    def test_creating_spell(self):
        spell = Spell("Fireball")
        assert spell.name == "Fireball"
        assert spell.dc == 0

    def test_adding_components_to_spell(self):
        fireball = Spell("Fireball")
        spell_element = self.spell_components.get_element("Combustion")
        fireball.add_component(spell_element)
        assert len(fireball.components) == 1
        assert fireball.dc != 0


class TestSpellBook:
    @classmethod
    def setup_class(cls):
        test_data = load_data("kbr_char/green.json")
        cls.spell_components = SpellComponentCollection(test_data)

        cls.test_spell = Spell("Fireball")
        spell_element = cls.spell_components.get_element("Combustion")
        cls.test_spell.add_component(spell_element)

    def setup_method(self):
        self.spellbook = SpellBook("Exodius")

    def test_spellbook_creation(self):
        assert self.spellbook.name == "Exodius"

    def test_adding_spell_to_spellbook(self):
        self.spellbook.add_spell(self.test_spell)
        assert self.spellbook.spells
        assert self.spellbook.spells[0].name == "Fireball"

    def test_retrieving_spell_from_spellbook(self):
        self.spellbook.add_spell(self.test_spell)
        fireball_spell = self.spellbook.get_spell("Fireball")
        assert fireball_spell.name == "Fireball"
        assert fireball_spell.dc != 0

    def test_retrieving_spell_name_list(self):
        self.spellbook.add_spell(self.test_spell)
        spell_name_list = self.spellbook.spell_list()
        assert spell_name_list
        assert spell_name_list[0] == "Fireball"

    def test_retrieving_spell_detailed_list(self):
        self.spellbook.add_spell(self.test_spell)
        spell_detailed_list = self.spellbook.detailed_spell_list()
        assert spell_detailed_list
        assert spell_detailed_list[0].name == "Fireball"
        assert spell_detailed_list[0].dc != 0

    def test_removing_spell_from_spellbook(self):
        self.spellbook.add_spell(self.test_spell)
        self.spellbook.remove_spell("Fireball")
        post_removal_spell_list = self.spellbook.spell_list()
        assert not post_removal_spell_list

    def test_exception_when_adding_two_spells_with_same_name(self):
        with pytest.raises(ValueError):
            self.spellbook.add_spell(self.test_spell)
            self.spellbook.add_spell(self.test_spell)


class TestCalc:

    test_cases = [
        ("1+2", 3),
        ("3+4+5", 12),
        ("7-6", 1),
        ("10-8-9", -7),
        ("5*5", 25),
        ("100*10*3", 3000),
        ("19/5", 3),
        ("1000/20/2", 25),
        ("2**3", 8),
        ("10-7+(3*5)/(10**2)", 3)
    ]

    @pytest.mark.parametrize("test_input,expected", test_cases)
    def test_formula(self, test_input, expected):
        assert int(Calc.evaluate(test_input)) == expected
