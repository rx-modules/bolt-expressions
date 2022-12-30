from bolt_expressions import Scoreboard

abc = Scoreboard("abc.main")

abc["@s"] = min(abc["@s"], 10)
abc["@s"] = max(abc["@s"], 20)

abc["@s"] = min(30, abc["@s"])
abc["@s"] = max(40, abc["@s"])

abc["$a"] = min(0, abc["$value"])
abc["$b"] = max(0, abc["$value"])

abc["$c"] = max(0, min(abc["$value"], 100))

abc["$d"] = min(abc["$a", "$b", "$c"])

abc["$e"] = min(abc["$m"], 4, abc["$n"], 0, -1, abc["$o"])
abc["$f"] = max(abc["$p"], 4, 3*abc["$q"], 0, -5, abc["$r"] - 1)