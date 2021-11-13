import os
import json
from kbr_char.spells import SpellFactory


class TestSpells:
    def setup_method(self):
        with open("kbr_char/spells.json") as f:
            test_config = json.load(f)
        self.codex = SpellFactory(test_config)
        self.save_file = "codex_test"

    def teardown_method(self):
        self.codex = None
        if os.path.isfile(self.save_file):
            os.remove(self.save_file)
        self.save_file = None

    def test_saving_spell_configurations(self):
        self.codex.save(self.save_file)
        assert os.path.isfile(self.save_file)

    def test_loading_spell_configuration(self):
        self.codex.save(self.save_file)
        SpellFactory.load(self.save_file)

    def test_spell_creation_and_dc_calculation(self):
        Fireball = self.codex.create_spell("fireball")
        Fireball.add_quality(self.codex.Combustion)
        Fireball.add_quality(self.codex.Blast)
        Fireball.add_quality(self.codex.SpellRange, 100)
        Fireball.add_quality(self.codex.Arrow)
        Fireball.add_quality(self.codex.EffectDistance, 20)
        assert Fireball.name == "fireball"
        assert Fireball.dc == 100
