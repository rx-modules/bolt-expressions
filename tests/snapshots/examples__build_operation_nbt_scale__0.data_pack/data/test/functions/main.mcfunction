say # scaled data to data
execute store result storage demo out int 100 run data get storage demo value 1
say # scaled score
execute store result storage demo out double 0.01 run scoreboard players get $value obj
say # scaled data
execute store result storage demo out double 0.01 run data get storage demo value 1
say # get and set scaled data
execute store result storage demo out double 1.0 run data get storage demo value 1
say # set scaled score
scoreboard players operation $i0 bolt.expr.temp = $value obj
execute store result storage demo out int 50 run scoreboard players add $i0 bolt.expr.temp 1
say # set scaled score
scoreboard players operation $i0 bolt.expr.temp = $value obj
execute store result storage demo out double 0.1 run scoreboard players add $i0 bolt.expr.temp 1
say # get scaled data
execute store result score $i0 bolt.expr.temp run data get storage demo value 100
execute store result storage demo out int 1 run scoreboard players add $i0 bolt.expr.temp 3
say # get scaled data, operate and set it back scaled down
execute store result score $i0 bolt.expr.temp run data get storage demo value 100
execute store result storage demo out double 0.01 run scoreboard players add $i0 bolt.expr.temp 5
say # get scaled data
execute store result score #offset obj run data get entity @s Motion[0] 100
scoreboard players operation #offset obj -= #x obj
say # append scaled score
scoreboard players operation $i0 bolt.expr.temp = $value obj
data modify storage demo list append value 0
execute store result storage demo list[-1] double 0.01 run scoreboard players get $i0 bolt.expr.temp
say # prepend scaled score
scoreboard players operation $i0 bolt.expr.temp = $value obj
data modify storage demo list prepend value 0
execute store result storage demo list[0] int 100 run scoreboard players get $i0 bolt.expr.temp
say # insert scaled score
scoreboard players operation $i0 bolt.expr.temp = $value obj
data modify storage demo list insert 3 value 0
execute store result storage demo list[3] int 100 run scoreboard players get $i0 bolt.expr.temp
