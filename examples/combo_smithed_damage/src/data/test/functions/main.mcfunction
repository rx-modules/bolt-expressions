from bolt_expressions import Scoreboard

Objective = ctx.inject(Scoreboard)

smithed_damage = Objective("smithed.damage")
damage = smithed_damage["damage"]
toughness = smithed_damage["toughness"]
armor = smithed_damage["armor"]

atf = (10 * armor - (400 * damage / (80 + 10 * toughness)))
maxxed = max((10 * armor) / 5, atf)
damage *= (250 - (min(200, maxxed))) / 25
