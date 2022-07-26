from bolt_expressions import Scoreboard, Data

obj = Scoreboard("obj")
temp = Data.storage("demo")
player = Data.entity("@s")

temp.value = Data.cast(obj["$a"], "byte")

temp.pos[0] = Data.cast(obj["$x"] / 100, "double")

n = Data.cast(obj["$n"], "int")

temp.n = n
temp.m = Data.cast(n, "float")


temp.x = Data.cast((temp.x*100 + 1) / 100, "double")
temp.num = Data.cast(temp.num*100 + 1, "double") / 100

s = Data.cast(obj["$val"], "short")
temp.a = s * 100
temp.a = s / 10

temp.a = (obj["$a"] + 1)
temp.a = Data.cast(obj["$b"] + 2, "double") / 10

say nicer
temp.foo = Data.cast(obj["$foo"] / 100, "double")

temp.bar = temp.foo

temp.bar = Data.cast(temp.foo, "double")

say temp.c will be scaled and converted to a double (preserve precision)
temp.bar = temp.c / 10

say force temp.c to be truncated
temp.bar = Data.cast(temp.c / 10, "int")