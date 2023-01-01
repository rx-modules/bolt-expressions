from bolt_expressions import Scoreboard, Data

abc = Scoreboard("abc.main")
storage = Data.storage(example:main)

a, b, c =  abc["$a", "$b", "$c"]

say min(1,2,3)
say min(2)
say min([], default=0)
say min([2], default=0)
say min([(0, 1, 3), (0, 1, 2)], default=0)
say max(1,2,3)
say max(2)
say max([], default=0)
say max([2], default=0)
say max([(0, 1, 3), (0, 1, 2)], default=0)

def _lambda(n):
    return n["x"]

say min({x:4}, {x:2}, {x:-4}, key=_lambda)
say max({x:4}, {x:2}, {x:-4}, key=_lambda)

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


storage.value = min(abc["$a"], storage.a, storage.b)

abc["$result"] = min(storage.a, storage.b, storage.c)