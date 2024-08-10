say # scaled data to data
execute store result storage demo out int 100 run data get storage demo value 1
say # scaled score
execute store result storage demo out double 0.01 run scoreboard players get $value obj
say # scaled data
execute store result storage demo out double 0.01 run data get storage demo value 1
say # get and set scaled data
execute store result score $i0 bolt.expr.temp run data get storage demo value 100
execute store result storage demo out double 0.01 run scoreboard players get $i0 bolt.expr.temp
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
data modify storage demo list append value 0
execute store result storage demo list[-1] double 0.01 run scoreboard players get $value obj
say # prepend scaled score
data modify storage demo list prepend value 0
execute store result storage demo list[0] int 100 run scoreboard players get $value obj
say # insert scaled score
data modify storage demo list insert 3 value 0
execute store result storage demo list[3] int 100 run scoreboard players get $value obj
scoreboard players operation $i0 bolt.expr.temp = ticks_since_death obj
execute store result score $i1 bolt.expr.temp run data get storage demo death_gametime 1
execute store result storage demo hours double 0.00001388888888888889 run scoreboard players operation $i0 bolt.expr.temp -= $i1 bolt.expr.temp
scoreboard players operation ticks_since_death obj %= $1200 bolt.expr.const
execute store result storage demo minutes double 0.0008333333333333334 run scoreboard players get ticks_since_death obj
scoreboard players operation ticks_since_death obj %= $20 bolt.expr.const
execute store result storage demo seconds double 0.05 run scoreboard players get ticks_since_death obj
