# kbr_char Project
## Intro
KBR stands for Knights of the Black Rose.
This is a custom setting for a Tabletop RPG. With the setting comes a custom magic system.
The goal of this is to create an easy to use interface to be a player in this custom system.

## Major Roadmap:
- Spell Creation:
  - [x] JSON configure spell options
  - [x] Track created spells
  - [x] Save and Load spells
  - [x] Figure DCs
  - [ ] Useful Description
  - [ ] CLI, importable, and gui?
- Character Creation:
  - [ ] JSON configure character options
  - [ ] Track characters
  - [ ] Save and Load characters
  - [ ] Useful descriptions
  - [ ] Attach spells
    - [ ] Make text to copy paste rolls into discord
  - [ ] Inventory management 
    - [ ] Weight
    - [ ] Money
    - [ ] Ammo
    - [ ] Weapons
      - [ ] Make copy paste text for rolls
      - [ ] Useful descriptions
      - [ ] Special ability reminders 

## Example Usage:
Load up a json file or string.

```Python
json_file = json.load("json file", "r")
```

Instance a spell making and storage class.

```Python
Codex = SpellFactory(json_file)
```

Saving a SpellFactory.

```Python
Codex.save("codex_file")
```

Loading a SpellFactory.

```Python
Codex.load("codex_file")
```


Create your spell!
```Python
Fireball = Codex.create_spell("fireball") # Assigns a spell to a variable, gives it a name for later, and saves it to the SpellFactory
Fireball.add_quality(Codex.Combustion) # Combustion!
Fireball.add_quality(Codex.SpellRange, 100) # Let us add a bit of range, 100ft should be pretty good.
Fireball.add_quality(Codex.Bomb) # Loads up the "bomb" shape for an explosion!
Fireball.add_quality(Codex.EffectDistance, 20) # 20ft Bomb area will take care of things

Fireball.dc # Returns the DC to roll to cast our awesome fireball!
