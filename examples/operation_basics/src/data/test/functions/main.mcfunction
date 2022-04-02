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


value = temp["#value"]

if score value.scoreholder value.objective matches 100..:
    value = 0

if score value.holder value.obj matches 100..:
    value = 0

store result score value.holder value.obj:
    temp["#foo"] += 1