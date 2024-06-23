from nbtlib import Compound, Path, Byte, Short
from bolt_expressions import Scoreboard, Data, Expression
from bolt_expressions.utils import assert_exception
from typing import Any

temp = Data.storage(demo:temp)
obj = Scoreboard("obj.temp")


ab_mean = (obj["$a"] + obj["$b"]) / 2
result = ab_mean % obj["$d"]

say str(ab_mean)
say str(result)

obj["$result"] = result * 100
obj["$x"] = ab_mean

say type(ab_mean)
say ab_mean.is_lazy()

obj["$t"] = ab_mean

ab_mean.evaluate()

# each line becomes a single set operation
obj["$u"] = ab_mean
obj["$v"] = ab_mean
obj["$w"] = ab_mean

# not lazy anymore
say ab_mean.is_lazy()

# evaluating it again does nothing
ab_mean.evaluate()



# merge operation is implicitly evaluated before accessing "color"
color = (temp.default_fields | temp.current_fields).color[list[Byte]]
color[0] = 127
temp.output_color = color

items = temp.chest1 | temp.chest2 | temp.chest3

items.merge({})
items.merge({})


r = (obj["$a"] + 2) - obj["$b"]

# r is expanded
obj["@s"] = r

# implicitly evaluation (even though enabling a fake player score does not make sense)
r.enable()

# r is no longer set
obj["$a1"] = r
obj["$a2"] = r

tellraw @a (obj["@s"] * 5)

v = (obj["$v"] * 5) / obj["$w"]
obj["$v"] = 0
if score var v matches 1.. say Hello 


def static_vars(f):
  def score_format(i: int):
    return f"${f.__name__}{i}"
  def data_format(i: int):
    return f"{f.__name__}{i}"

  def decorated(*args, **kwargs):
    with Expression.temp_score.override(format=score_format, reset=True), Expression.temp_data.override(format=data_format, reset=True):
      return f(*args, **kwargs)
  
  return decorated

@static_vars
def sum(a, b):
  execute function ~/sum:
    r = a + b
    r += 5

    if temp.arr[0] == 0:
      a = r

  return r


a, b = obj["$a", "$b"]

sum(a, b)
sum(a, b)