execute store result score $i0 bolt.expr.temp run data get entity @s Health 1
scoreboard players operation @s abc.main += $i0 bolt.expr.temp
execute store result score $i0 bolt.expr.temp run data get entity rx97 SelectedItem.Count 1
scoreboard players operation @s abc.main -= $i0 bolt.expr.temp
execute store result score $i0 bolt.expr.temp run data get entity TheWii SelectedItem.Damage 1
scoreboard players operation @s abc.main *= $i0 bolt.expr.temp
execute store result score $i0 bolt.expr.temp run data get block 0 0 0 RecordItem.data 1
scoreboard players operation @s abc.main /= $i0 bolt.expr.temp
execute store result score $i0 bolt.expr.temp run data get block ~1 ~2 ~3 Items[0] 1
scoreboard players operation @s abc.main %= $i0 bolt.expr.temp
data modify storage demo:prefix/temp foo set from storage demo:prefix/temp bar
execute store result score $i0 bolt.expr.temp run data get storage demo:prefix/temp player 1
execute store result score $i1 bolt.expr.temp run data get entity @s Health 1
execute store result storage demo:prefix/temp player int 1 run scoreboard players operation $i0 bolt.expr.temp += $i1 bolt.expr.temp
execute store result score $i0 bolt.expr.temp run data get storage demo:prefix/temp player 1
execute store result score $i1 bolt.expr.temp run data get entity rx97 SelectedItem.Count 1
execute store result storage demo:prefix/temp player int 1 run scoreboard players operation $i0 bolt.expr.temp -= $i1 bolt.expr.temp
execute store result score $i0 bolt.expr.temp run data get storage demo:prefix/temp player 1
execute store result score $i1 bolt.expr.temp run data get entity TheWii SelectedItem.Damage 1
execute store result storage demo:prefix/temp player int 1 run scoreboard players operation $i0 bolt.expr.temp *= $i1 bolt.expr.temp
execute store result score $i0 bolt.expr.temp run data get storage demo:prefix/temp player 1
execute store result score $i1 bolt.expr.temp run data get block 0 0 0 RecordItem.data 1
execute store result storage demo:prefix/temp player int 1 run scoreboard players operation $i0 bolt.expr.temp /= $i1 bolt.expr.temp
execute store result score $i0 bolt.expr.temp run data get storage demo:prefix/temp player 1
execute store result score $i1 bolt.expr.temp run data get block ~1 ~2 ~3 Items[0] 1
execute store result storage demo:prefix/temp player int 1 run scoreboard players operation $i0 bolt.expr.temp %= $i1 bolt.expr.temp
execute store result score $i0 bolt.expr.temp run data get block ~1 ~2 ~3 Items[-1].Count 1
execute store result score $i1 bolt.expr.temp run data get entity @s SelectedItem.Count 1
execute store result block ~1 ~2 ~3 Items[-1].Count int 1 run scoreboard players operation $i0 bolt.expr.temp += $i1 bolt.expr.temp
