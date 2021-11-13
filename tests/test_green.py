import pytest
from kbr_char.green import (
    Modifier,
    load_data,
    SpellComponentCollection,
    Spell,
    Element,
    Range,
    Shape,
    SpellComponent,
    SpellBook,
)


class TestSpellComponentCollections:
    @classmethod
    def setup_class(cls):
        test_data = load_data("kbr_char/green.json")
        cls.spell_components = SpellComponentCollection(test_data)

    def test_retrieving_a_component(self):
        spell_component = self.spell_components.get_component(Element, "Combustion")
        assert spell_component.name == "Combustion"

    def test_exception_when_retrieving_a_nonexistant_component_name(self):
        with pytest.raises(IndexError):
            self.spell_components.get_component(Element, "NonExistant")

    def test_retrieve_list_of_components_by_type(self):
        def retrieve_component_type(comp_type: SpellComponent) -> list[SpellComponent]:
            return self.spell_components.get_components_by_type(comp_type)

        elements = retrieve_component_type(Element)
        assert elements

        ranges = retrieve_component_type(Range)
        assert ranges

        shapes = retrieve_component_type(Shape)
        assert shapes

        modifiers = retrieve_component_type(Modifier)
        assert modifiers

    def test_retrieve_list_of_components_by_name(self):
        spell_component = self.spell_components.get_components_by_name("Combustion")
        assert spell_component
        assert spell_component[0].name == "Combustion"


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
        spell_element = self.spell_components.get_component(Element, "Combustion")
        fireball.add_component(spell_element)
        assert len(fireball.components) == 1
        assert fireball.dc != 0


class TestSpellBook:
    @classmethod
    def setup_class(cls):
        test_data = load_data("kbr_char/green.json")
        cls.spell_components = SpellComponentCollection(test_data)

        cls.test_spell = Spell("Fireball")
        spell_element = cls.spell_components.get_component(Element, "Combustion")
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