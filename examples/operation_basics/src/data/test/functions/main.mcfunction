from bolt_expressions import Scoreboard
Objective = ctx.inject(Scoreboard)

abc = Objective("abc.main")
temp = Objective("abc.temp")

function ./operations:
    abc["@s"] += temp["@s"]
    abc["@s"] -= temp["@s"]
    abc["@s"] *= temp["@s"]
    abc["@s"] /= temp["@s"]
    abc["@s"] %= temp["@s"]

function ./constants:
    abc["@s"] += 10
    abc["@s"] -= 20
    abc["@s"] *= 30
    abc["@s"] /= 40
    abc["@s"] %= 50
