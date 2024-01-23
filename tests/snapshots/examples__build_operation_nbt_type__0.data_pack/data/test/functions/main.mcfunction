execute store result storage bolt.expr:temp 2384k242hd495_0 byte 1 run scoreboard players get $a obj
data modify storage demo value set from storage bolt.expr:temp 2384k242hd495_0
execute store result storage bolt.expr:temp 2384k242hd495_1 double 0.01 run scoreboard players get $x obj
data modify storage demo pos[0] set from storage bolt.expr:temp 2384k242hd495_1
execute store result storage bolt.expr:temp 2384k242hd495_2 int 1 run scoreboard players get $n obj
data modify storage demo n set from storage bolt.expr:temp 2384k242hd495_2
execute store result storage bolt.expr:temp 2384k242hd495_3 float 1 run data get storage bolt.expr:temp 2384k242hd495_2 1
data modify storage demo m set from storage bolt.expr:temp 2384k242hd495_3
execute store result score $i0 bolt.expr.temp run data get storage demo x 100
scoreboard players add $i0 bolt.expr.temp 1
execute store result storage bolt.expr:temp 2384k242hd495_4 double 0.01 run scoreboard players get $i0 bolt.expr.temp
data modify storage demo x set from storage bolt.expr:temp 2384k242hd495_4
execute store result score $i0 bolt.expr.temp run data get storage demo num 100
scoreboard players add $i0 bolt.expr.temp 1
execute store result storage bolt.expr:temp 2384k242hd495_5 double 1 run scoreboard players get $i0 bolt.expr.temp
execute store result storage demo num double 0.01 run data get storage bolt.expr:temp 2384k242hd495_5 1
execute store result storage bolt.expr:temp 2384k242hd495_6 short 1 run scoreboard players get $val obj
execute store result storage demo a int 100 run data get storage bolt.expr:temp 2384k242hd495_6 1
execute store result storage demo a double 0.1 run data get storage bolt.expr:temp 2384k242hd495_6 1
scoreboard players operation $i0 bolt.expr.temp = $a obj
scoreboard players add $i0 bolt.expr.temp 1
execute store result storage demo a int 1 run scoreboard players get $i0 bolt.expr.temp
scoreboard players operation $i0 bolt.expr.temp = $b obj
scoreboard players add $i0 bolt.expr.temp 2
execute store result storage bolt.expr:temp 2384k242hd495_7 double 1 run scoreboard players get $i0 bolt.expr.temp
execute store result storage demo a double 0.1 run data get storage bolt.expr:temp 2384k242hd495_7 1
say nicer
execute store result storage bolt.expr:temp 2384k242hd495_8 double 0.01 run scoreboard players get $foo obj
data modify storage demo foo set from storage bolt.expr:temp 2384k242hd495_8
data modify storage demo bar set from storage demo foo
execute store result storage bolt.expr:temp 2384k242hd495_9 double 1 run data get storage demo foo 1
data modify storage demo bar set from storage bolt.expr:temp 2384k242hd495_9
say temp.c will be scaled and converted to a double (preserve precision)
execute store result storage demo bar double 0.1 run data get storage demo c 1
say force temp.c to be truncated
execute store result storage bolt.expr:temp 2384k242hd495_10 int 0.1 run data get storage demo c 1
data modify storage demo bar set from storage bolt.expr:temp 2384k242hd495_10
say score is casted to int
execute store result storage demo value int 1 run scoreboard players get @s obj
say score is casted to double
execute store result storage demo value double 0.1 run scoreboard players get @s obj
execute store result storage demo value byte 1 run scoreboard players get @s obj
execute store result score $i0 bolt.expr.temp run data get storage demo x1 100
execute store result score $i1 bolt.expr.temp run data get storage demo x2 100
scoreboard players operation $i0 bolt.expr.temp += $i1 bolt.expr.temp
execute store result storage demo value double 0.005 run scoreboard players get $i0 bolt.expr.temp
say casting to byte before appending to list
execute store result storage demo value byte 1 run scoreboard players get $value obj
data modify storage demo list append from storage demo value
say or use Data.cast
execute store result storage bolt.expr:temp 2384k242hd495_11 byte 1 run scoreboard players get $value obj
data modify storage demo list append from storage bolt.expr:temp 2384k242hd495_11
say casts y to double
execute store result storage demo x double 1 run data get storage demo y 1
say only copies the value
data modify storage demo x set from storage demo y
say no cast
data modify storage demo x set from storage demo z
execute store result storage demo x double 1 run data get storage demo z 1
say casts z to double
say no cast (type of x is temporarely overwritten)
data modify storage demo x set from storage demo arbitrary
say casts to a double
execute store result storage demo x double 1 run data get storage demo arbitrary 1
