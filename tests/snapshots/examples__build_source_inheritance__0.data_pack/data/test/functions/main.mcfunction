data modify storage example:main b.index[0].named."! 3  - b#2a".a{x: 1}.b[{y: 2}].c[] set value 3
execute store result score $i0 bolt.expr.temp run data get storage example:main value 1
scoreboard players add $i0 bolt.expr.temp 1
execute store result storage example:main value int 1 run scoreboard players get $i0 bolt.expr.temp
scoreboard players operation $a obj.temp = $value obj.temp
execute store result score $i0 bolt.expr.temp run data get storage example:main a 1
scoreboard players operation $a obj.temp -= $i0 bolt.expr.temp
execute store result storage example:main a int 1 run scoreboard players get $a obj.temp
execute unless data storage example:main {a: 0} run say It's 0!
execute if data storage example:main {a: 0} run say It's not 0...
