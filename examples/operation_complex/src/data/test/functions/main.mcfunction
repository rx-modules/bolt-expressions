from bolt_expressions import Scoreboard
Objective = ctx.inject(Scoreboard)

abc = Objective("abc.main")

abc["my_var"] = (abc["@s"] + abc["@e"]) * 5 + abc["@s"] * 2
