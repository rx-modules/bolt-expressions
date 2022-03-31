from bolt_expressions import Scoreboard

abc = Scoreboard("abc.main")
temp = Scoreboard("abc.temp")

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
