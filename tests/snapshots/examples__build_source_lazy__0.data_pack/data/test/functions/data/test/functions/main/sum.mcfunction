scoreboard players operation $sum0 bolt.expr.temp = $a obj.temp
scoreboard players operation $sum0 bolt.expr.temp += $b obj.temp
scoreboard players add $sum0 bolt.expr.temp 5
data remove storage bolt.expr:temp sum1
data modify storage bolt.expr:temp sum1 set from storage demo:temp arr[0]
execute if data storage bolt.expr:temp {sum1: 0} run scoreboard players operation $a obj.temp = $sum0 bolt.expr.temp
