from bolt_expressions import Scoreboard

Objective = ctx.inject(Scoreboard)
abc = Objective("abc.main")

abc["@s"] += 10

# "output_score_replacement" ignores the first line
# scoreboard players operation $i0 temp = @s abc.main
#abc["@s"] = 3 * (2 * (abc["@s"] * abc["#val"]))

# fails to optimize because abc["@s"] is in the right side
# of addition, moving the output source reference to the
# second command
#abc["@s"] = 3 * (abc["#val"] + abc["@s"])

# "output_score_replacement" thrives with this one!
#abc["@s"] = 2 + 3 * (4 * (abc["@s"] + abc["#val"]))


#abc["#value"] = 2 + (5 * abc["#value"]) / 2
#abc["#value"] -= (1 + abc["@s"])

abc["@s"] *= abc["@s"]

#abc["@s"] *= abc["@s"]

#add = 10 * (abc["#value"] + 2)
#abc["@s"] = add * 2

#abc["@s"] += 10 * (abc["#val"] + 2)


# Noncommutative set collapsing might help here
#abc["@s"] -= abc["#val"] + 1

# Also here (Accidentaly heh)
#abc["@s"] *= abc["@s"]

# Here it falls back to Commutative set collapsing
#abc["@s"] *= (abc["@s"] + 1)

#
 # uid = Objective("rx.uid")
 #
 # uid["@s"] += 10 * (2 * uid["value"] / 10)
 #
 #
 #def minn(arg1, arg2):
 #    return arg1 < arg2
 #
 #def maxx(arg1, arg2):
 #    return arg1 > arg2
 #
 #smithed_damage = Objective("smithed.damage")
 #
 # smithed_damage["max"] = maxx(smithed_damage["@s"], 10)
 #
 ## smithed_damage = Objective("smithed.damage")
 #damage = smithed_damage["damage"]
 #toughness = smithed_damage["toughness"]
 #armor = smithed_damage["armor"]
 #
 #atf = (10 * armor - (400 * damage / (80 + 10 * toughness)))
 #maxxed = maxx((10 * armor) / 5, atf)
 #damage = damage * (250 - (minn(200, maxxed))) / 25
 #
 #smithed_damage = Objective("smithed.damage")
 #
 #
 # atf = (10 * smithed_damage["armor"] - (400 * smithed_damage["damage"] / (80 + 10 * smithed_damage["toughness"])))
 # maxxed = max((10 * smithed_damage["armor"]) / 5, atf)
 # smithed_damage["damage"] = smithed_damage["damage"] * (250 - (min(200, maxxed))) / 25
 #
 #/ damage = #damage * (250 - (min(200, max( 10armor ÷ 5   , #10ATF ))) / 25
 #
 # # normal set
 # uid["@s"] = 5
 #
 # # # normal set
 # uid["@s"] += 5
 # uid["@s"] += uid["@s"]
 #
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
 