execute store result score $i36 bolt.expr.temp run data get entity @s Health 1
scoreboard players operation @s abc.main += $i36 bolt.expr.temp
execute store result score $i38 bolt.expr.temp run data get entity rx97 SelectedItem.Count 1
scoreboard players operation @s abc.main -= $i38 bolt.expr.temp
execute store result score $i40 bolt.expr.temp run data get entity TheWii SelectedItem.Damage 1
scoreboard players operation @s abc.main *= $i40 bolt.expr.temp
execute store result score $i42 bolt.expr.temp run data get block 0 0 0 RecordItem.data 1
scoreboard players operation @s abc.main /= $i42 bolt.expr.temp
execute store result score $i44 bolt.expr.temp run data get block ~1 ~2 ~3 Items[0] 1
scoreboard players operation @s abc.main %= $i44 bolt.expr.temp
data modify storage demo:prefix/temp foo set from storage demo:prefix/temp bar
execute store result score $i46 bolt.expr.temp run data get storage demo:prefix/temp player 1
execute store result score $i47 bolt.expr.temp run data get entity @s Health 1
scoreboard players operation $i46 bolt.expr.temp += $i47 bolt.expr.temp
execute store result storage demo:prefix/temp player int 1 run scoreboard players get $i46 bolt.expr.temp
execute store result score $i49 bolt.expr.temp run data get storage demo:prefix/temp player 1
execute store result score $i50 bolt.expr.temp run data get entity rx97 SelectedItem.Count 1
scoreboard players operation $i49 bolt.expr.temp -= $i50 bolt.expr.temp
execute store result storage demo:prefix/temp player int 1 run scoreboard players get $i49 bolt.expr.temp
execute store result score $i52 bolt.expr.temp run data get storage demo:prefix/temp player 1
execute store result score $i53 bolt.expr.temp run data get entity TheWii SelectedItem.Damage 1
scoreboard players operation $i52 bolt.expr.temp *= $i53 bolt.expr.temp
execute store result storage demo:prefix/temp player int 1 run scoreboard players get $i52 bolt.expr.temp
execute store result score $i55 bolt.expr.temp run data get storage demo:prefix/temp player 1
execute store result score $i56 bolt.expr.temp run data get block 0 0 0 RecordItem.data 1
scoreboard players operation $i55 bolt.expr.temp /= $i56 bolt.expr.temp
execute store result storage demo:prefix/temp player int 1 run scoreboard players get $i55 bolt.expr.temp
execute store result score $i58 bolt.expr.temp run data get storage demo:prefix/temp player 1
execute store result score $i59 bolt.expr.temp run data get block ~1 ~2 ~3 Items[0] 1
scoreboard players operation $i58 bolt.expr.temp %= $i59 bolt.expr.temp
execute store result storage demo:prefix/temp player int 1 run scoreboard players get $i58 bolt.expr.temp
execute store result score $i61 bolt.expr.temp run data get block ~1 ~2 ~3 Items[-1].Count 1
execute store result score $i62 bolt.expr.temp run data get entity @s SelectedItem.Count 1
scoreboard players operation $i61 bolt.expr.temp += $i62 bolt.expr.temp
execute store result block ~1 ~2 ~3 Items[-1].Count int 1 run scoreboard players get $i61 bolt.expr.temp
