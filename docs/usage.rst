.. highlight:: python

=====
Usage
=====

To use kbr_char in a project

Load up a json file or string.
.. code-block::
    json_file = json.load("json file", "r")

Instance a spell making and storage class.
.. code-block::
    Codex = SpellFactory(json_file)


Saving a SpellFactory.
.. code-block::
    Codex.save("codex_file")


Loading a SpellFactory.
.. code-block::
    Codex.load("codex_file")



Create your spell!
.. code-block::
    Fireball = Codex.create_spell("fireball") # Assigns a spell to a variable, gives it a name for later, and saves it to the SpellFactory
    Fireball.add_quality(Codex.Combustion) # Combustion!
    Fireball.add_quality(Codex.SpellRange, 100) # Let us add a bit of range, 100ft should be pretty good.
    Fireball.add_quality(Codex.Bomb) # Loads up the "bomb" shape for an explosion!
    Fireball.add_quality(Codex.EffectDistance, 20) # 20ft Bomb area will take care of things
    Fireball.dc # Returns the DC to roll to cast our awesome fireball!
