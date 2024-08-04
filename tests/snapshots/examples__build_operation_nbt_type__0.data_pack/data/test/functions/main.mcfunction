execute store result storage demo value byte 1 run scoreboard players get $a obj
execute store result storage demo pos[0] double 0.01 run scoreboard players get $x obj
execute store result storage bolt.expr:temp 2384k242hd495_5 int 1 run scoreboard players get $n obj
data modify storage demo n set from storage bolt.expr:temp 2384k242hd495_5
execute store result storage demo m float 1 run data get storage bolt.expr:temp 2384k242hd495_5 1
execute store result score $i0 bolt.expr.temp run data get storage demo x 100
execute store result storage bolt.expr:temp i0 double 0.01 run scoreboard players add $i0 bolt.expr.temp 1
data modify storage demo x set from storage bolt.expr:temp i0
execute store result score $i0 bolt.expr.temp run data get storage demo num 100
execute store result storage bolt.expr:temp 2384k242hd495_32 short 1 run scoreboard players get $val obj
execute store result storage demo a int 100 run data get storage bolt.expr:temp 2384k242hd495_32 1
execute store result storage demo a double 0.1 run data get storage bolt.expr:temp 2384k242hd495_32 1
scoreboard players operation $i0 bolt.expr.temp = $a obj
execute store result storage demo a int 1 run scoreboard players add $i0 bolt.expr.temp 1
scoreboard players operation $i0 bolt.expr.temp = $b obj
say nicer
execute store result storage demo foo double 0.01 run scoreboard players get $foo obj
data modify storage demo bar set from storage demo foo
execute store result storage demo bar double 1 run data get storage demo foo 1
say temp.c will be scaled and converted to a double (preserve precision)
execute store result storage demo bar double 0.1 run data get storage demo c 1
say force temp.c to be truncated
execute store result storage demo bar int 0.1 run data get storage demo c 1
say score is casted to int
execute store result storage demo value int 1 run scoreboard players get @s obj
say score is casted to double
execute store result storage demo value double 0.1 run scoreboard players get @s obj
execute store result storage demo value byte 1 run scoreboard players get @s obj
execute store result score $i0 bolt.expr.temp run data get storage demo x1 100
execute store result score $i1 bolt.expr.temp run data get storage demo x2 100
execute store result storage demo value double 0.005 run scoreboard players operation $i0 bolt.expr.temp += $i1 bolt.expr.temp
say casting to byte before appending to list
execute store result storage demo value byte 1 run scoreboard players get $value obj
data modify storage demo list append from storage demo value
say or use Data.cast
execute store result storage bolt.expr:temp i0 byte 1 run scoreboard players get $value obj
data modify storage demo list append from storage bolt.expr:temp i0
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
execute store result storage demo elements[0] double 0.1 run scoreboard players get $value obj
execute store result storage demo elements[0] double 0.1 run scoreboard players get $value obj
