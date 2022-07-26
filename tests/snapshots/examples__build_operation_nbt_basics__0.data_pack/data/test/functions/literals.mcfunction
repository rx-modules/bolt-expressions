data modify entity @s Health set value 10
execute store result score $i0 bolt.expr.temp run data get entity @s Health 1
scoreboard players add $i0 bolt.expr.temp 20
execute store result entity @s Health int 1 run scoreboard players get $i0 bolt.expr.temp
execute store result score $i0 bolt.expr.temp run data get entity rx97 Health 1
scoreboard players remove $i0 bolt.expr.temp 30
execute store result entity rx97 Health int 1 run scoreboard players get $i0 bolt.expr.temp
execute store result block 0 0 0 data.ur_mom int 40 run data get block 0 0 0 data.ur_mom 1
execute store result block ~1 ~2 ~3 Items[0].Count double 0.02 run data get block ~1 ~2 ~3 Items[0].Count 1
execute store result score $i0 bolt.expr.temp run data get entity TheWii Inventory[{Slot: -103b}].tag.data.bolt 1
scoreboard players operation $i0 bolt.expr.temp %= $60 bolt.expr.const
execute store result entity TheWii Inventory[{Slot: -103b}].tag.data.bolt int 1 run scoreboard players get $i0 bolt.expr.temp
data modify entity @s Inventory[].tag.string set value "your mom"
data modify entity @s Inventory[].tag.int set value 10
data modify entity @s Inventory[].tag.float set value 10.0f
data modify entity @s Inventory[].tag.double set value 10.0d
data modify entity @s Inventory[].tag.list set value []
data modify entity @s Inventory[].tag.list set value [1, 2, 3]
data modify entity @s Inventory[].tag.list set value [1, 2, 3, 4, 5, 6]
data modify entity @s Inventory[].tag.list set value [{}, {}, {}]
data modify entity @s Inventory[].tag.list set value [{bar: 2.5f}, {baz: 0b}]
data modify entity @s Inventory[].tag.list set value {}
data modify entity @s Inventory[].tag.list set value {foo: 2, baz: -1s}
