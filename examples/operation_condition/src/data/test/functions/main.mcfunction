from bolt_expressions import Scoreboard, Data, Expression

obj = Scoreboard("obj")
storage = Data.storage(./temp)

a, b, c, d, e, r = obj["$a", "$b", "$c", "$d", "$e", "$r"]
w, x, y, z = (storage.w, storage.x, storage.y, storage.z)

r = not a
r = not (not a)

r = a == 0
r = a != 0
r = a == b

say "a > b > c"

say using addition
r = ( (a > b) + (b > c) ) == 2

say using branch
r = 0
if a > b:
    if b > c:
        r = 1

say using and
if a > b and b > c:
    say yes

if not a > b:
    say a is less than or equal to b or either a or b does not exist

a = x == 0
a = x <= 0
a = x > y

if (a + b) > 0:
  a = 1
else:
  say a is not zero

if a > 0:
  say a is positive

if (a + b) > 0:
  b = 0
else:
  a = 1

if a:
  say value exists
elif storage.x:
  say x exists
else:
  say it does not exist

c = (a + 5) > 0 or b

if a:
  say it's a!
elif b:
  say it's b!
elif c:
  say it's c!
elif d:
  say it's d!
else:
  say idk

if storage.x == obj["$a"]:
  say "a"
elif obj["$a"] == storage.x:
  say "b"
elif storage.x == storage.y:
  say "c"
elif storage.x == 5:
  say "d"
elif storage.x[0] == 5:
  say "e"
elif storage.x == "hello":
  say "f"
elif storage.x == [1,2,3]:
  say "g"
elif storage.x == {}:
  say "h"
