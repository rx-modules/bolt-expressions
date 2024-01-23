from bolt_expressions import Scoreboard, Data
from nbtlib import Byte, Short, Int, Long, Float, Double
from typing import Any

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


say score is casted to int
temp.value = obj["@s"]
say score is casted to double
temp.value = obj["@s"] / 10

temp.value[Byte] = obj["@s"]

temp.value[Double] = (temp.x1 * 100 + temp.x2 * 100) / 200


say casting to byte before appending to list
temp.value[Byte] = obj['$value']
temp.list.append(temp.value)

say or use Data.cast
temp.list.append(Data.cast(obj['$value'], Byte))


x = temp.x[Double]

say casts y to double
x = temp.y

say only copies the value
x = temp.y[Double]


z = temp.z[Double]

say no cast
x = z

x = z[Any]
say casts z to double

say no cast (type of x is temporarely overwritten)
x[Any] = temp.arbitrary

say casts to a double
x = temp.arbitrary
