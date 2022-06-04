from bolt_expressions import Scoreboard

abc = Scoreboard("abc.main")

abc["@s"] += 10

foo = Scoreboard("obj.random", "$foo")
foo = 4

major, minor, patch = Scoreboard("load.status", "#pack.major", "#pack.minor", "#pack.patch")
major = 1
minor = 18
patch = 2

x, y, z = abc["$x", "$y", "$z"]
x = 0
y = 1
z = 2