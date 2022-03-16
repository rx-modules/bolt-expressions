from pointers import Scoreboard

tellraw @a "Hello World"
Objective = ctx.inject(Scoreboard)

uid = Objective("rx.uid")

uid["@s"] += 10 * (2 * uid["#value"] / 10)

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
