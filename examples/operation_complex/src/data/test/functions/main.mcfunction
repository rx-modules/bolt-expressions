from bolt_expressions import Scoreboard

abc = Scoreboard("abc.main")

abc["my_var"] = (abc["@s"] + abc["@e"]) * 5 + abc["@s"] * 2
