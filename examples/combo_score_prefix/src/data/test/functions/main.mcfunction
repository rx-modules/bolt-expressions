from bolt_expressions import Scoreboard

abc = Scoreboard("abc.obj")


if score var (abc["@s"] % 5) matches 0

abc["@s"] = (abc["#value"] * 2 + 1) / (abc["#denom"] * 5)
abc["@s"] = abc["#value"] * 3 * 4 * 6 * 7 * 8
abc["@s"] = abc["#value"] * -5
abc["@s"] += 10 + abc["#value"] * 123
abc["@s"] %= 50 + abc["#value"] * 0
