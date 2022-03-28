from bolt_expressions import Scoreboard

Objective = ctx.inject(Scoreboard)
abc = Objective("abc.main")

abc["@s"] = min(abc["@s"], 20)
