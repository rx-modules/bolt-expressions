from bolt_expressions import Scoreboard

smithed_damage = Scoreboard("smithed.damage")
_damage = smithed_damage["damage"]
toughness = smithed_damage["toughness"]
armor = smithed_damage["armor"]

atf = (10 * armor - (400 * _damage / (80 + 10 * toughness)))
maxxed = max((10 * armor) / 5, atf)
_damage *= (250 - (min(200, maxxed))) / 25
