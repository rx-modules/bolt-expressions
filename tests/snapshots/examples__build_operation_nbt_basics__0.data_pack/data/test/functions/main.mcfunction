execute store result score @s abc.main run data get storage demo:prefix/temp items
execute store result storage demo:prefix/temp value short 1 run data get storage demo:prefix/temp items
execute store result score $x abc.main run data get storage demo:prefix/temp a
execute store result score $i0 bolt.expr.temp run data get storage demo:prefix/temp b
scoreboard players operation $x abc.main += $i0 bolt.expr.temp
