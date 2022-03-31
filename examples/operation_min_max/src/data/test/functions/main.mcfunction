from bolt_expressions import Scoreboard

abc = Scoreboard("abc.main")

abc["@s"] = min(abc["@s"], 10)
abc["@s"] = max(abc["@s"], 20)

abc["@s"] = min(30, abc["@s"])
abc["@s"] = max(40, abc["@s"])
