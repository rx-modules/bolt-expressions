from bolt_expressions import Scoreboard

abc = Scoreboard("abc.main")

abc["@s"] += 10

obj = Scoreboard("obj.random")

foo = obj["$foo"]
foo = 4

load = Scoreboard("load.status", "dummy")

major, minor, patch = load["#pack.major", "#pack.minor", "#pack.patch"]

major = 1
minor = 18
patch = 2

x, y, z = abc["$x", "$y", "$z"]
x = 0
y = 1
z = 2


settings = Scoreboard("abc.settings", "trigger")

settings["@a"].enable()


Scoreboard("abc.settings", "trigger")