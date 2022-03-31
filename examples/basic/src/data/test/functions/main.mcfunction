from bolt_expressions import Scoreboard, Data

Objective = ctx.inject(Scoreboard)

abc = Objective("abc.main")

abc["@s"] += 10
