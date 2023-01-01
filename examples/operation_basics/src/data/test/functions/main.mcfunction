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

    abc["$a"] *= 1
    abc["$a"] *= -1

    abc["$b"] /= 1
    abc["$b"] /= -1

    abc["$c"] *= 0.5
    abc["$d"] *= 0.1
    abc["$e"] *= 0.123
    abc["$f"] *= 3.14
    abc["$g"] *= 0.494120

    abc["$h"] /= 0.5
    abc["$i"] /= 0.33
    abc["$j"] /= 1.5


value = temp["#value"]

if score value.scoreholder value.objective matches 100..:
    value = 0

if score value.holder value.obj matches 100..:
    value = 0

store result score value.holder value.obj:
    temp["#foo"] += 1