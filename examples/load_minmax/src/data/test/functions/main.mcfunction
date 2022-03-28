from bolt_expressions import Scoreboard, wrapped_min, wrapped_max

#/ TEMP SOLUTION
min = wrapped_min
max = wrapped_max

Objective = ctx.inject(Scoreboard)
abc = Objective("abc.main")

abc["@s"] = min(abc["@s"], 20)
