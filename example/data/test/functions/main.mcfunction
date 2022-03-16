from pointers import Scoreboard

tellraw @a "Hello World"

Objective = ctx.inject(Scoreboard)

#/ uid = Objective("rx.uid")

uid["@s"] += 10 * (2 * uid["value"] / 10)

# smithed_damage = Objective("smithed.damage")
# damage = smithed_damage["damage"]
# toughness = smithed_damage["toughness"]
# armor = smithed_damage["armor"]

# atf = (10 * armor - (400 * damage / (80 + 10 * toughness)))
# maxxed = max((10 * armor) / 5, atf)
# damage = damage * (250 - (min(200, maxxed))) / 25

# smithed_damage = Objective("smithed.damage")

# atf = (10 * smithed_damage["armor"] - (400 * smithed_damage["damage"] / (80 + 10 * smithed_damage["toughness"])))
# maxxed = max((10 * smithed_damage["armor"]) / 5, atf)
# smithed_damage["damage"] = smithed_damage["damage"] * (250 - (min(200, maxxed))) / 25

#/ damage = #damage * (250 - (min(200, max( 10armor ÷ 5   , #10ATF ))) / 25

# # normal set
# uid["@s"] = 5

# # # normal set
# uid["@s"] += 5
# uid["@s"] += uid["@s"]

# # mul + assignment
# uid["@s"] *= 5

# # # set from other
# uid["@s"] = uid["$current.id"]

#uid["my_var"] = (uid["@s"] + uid["@e"]) * 5 + uid["@s"] * 2

#/ io = objectives.create("io")  # assuming generate_namespace is set to rx.pdb
#/ io["@s"] = 5
#/ io["@s"] += io["@e[tag=other]"] * 2

# low key i kinda prefer
#/ io = Objective("io") over objectives.create()?
