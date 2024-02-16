scoreboard players set $r obj 0
execute store success score $r obj unless score $a obj matches ..-1 unless score $a obj matches 1..
scoreboard players set $r obj 0
execute store success score $r obj if score $a obj matches -2147483648.. unless score $a obj matches 0
execute store success score $r obj if score $a obj matches 0
execute store success score $r obj unless score $a obj matches 0
execute store success score $r obj if score $a obj = $b obj
scoreboard players set $i0 bolt.expr.temp 0
execute store success score $i0 bolt.expr.temp unless score $r obj matches ..-1 unless score $r obj matches 1..
scoreboard players add $i0 bolt.expr.temp 1
scoreboard players operation $r obj = $i0 bolt.expr.temp
say "a > b > c"
say using addition
execute store success score $i0 bolt.expr.temp if score $a obj > $b obj
execute store success score $i1 bolt.expr.temp if score $b obj > $c obj
scoreboard players operation $i0 bolt.expr.temp += $i1 bolt.expr.temp
execute store success score $r obj if score $i0 bolt.expr.temp matches 2
say using branch
scoreboard players set $r obj 0
execute if score $a obj > $b obj if score $b obj > $c obj run scoreboard players set $r obj 1
say using and
execute store success score $2384k242hd495_36 bolt.expr.temp if score $a obj > $b obj
execute if score $2384k242hd495_36 bolt.expr.temp matches -2147483648.. unless score $2384k242hd495_36 bolt.expr.temp matches 0 store success score $2384k242hd495_36 bolt.expr.temp if score $b obj > $c obj
execute if score $2384k242hd495_36 bolt.expr.temp matches -2147483648.. unless score $2384k242hd495_36 bolt.expr.temp matches 0 run say yes
execute unless score $a obj > $b obj run say a is less than or equal to b or either a or b does not exist
execute store success score $a obj if data storage test:temp {x: 0}
execute store result score $i0 bolt.expr.temp run data get storage test:temp x 1
execute store success score $a obj if score $i0 bolt.expr.temp matches ..0
execute store result score $i0 bolt.expr.temp run data get storage test:temp x 1
execute store result score $i1 bolt.expr.temp run data get storage test:temp y 1
execute store success score $a obj if score $i0 bolt.expr.temp > $i1 bolt.expr.temp
scoreboard players operation $i0 bolt.expr.temp = $a obj
scoreboard players operation $i0 bolt.expr.temp += $b obj
execute store success score $2384k242hd495_60 bolt.expr.temp if score $i0 bolt.expr.temp matches 1..
execute unless score $2384k242hd495_60 bolt.expr.temp matches 0 run scoreboard players set $a obj 1
execute if score $2384k242hd495_60 bolt.expr.temp matches 0 run say a is not zero
execute if score $a obj matches 1.. run say a is positive
scoreboard players operation $i0 bolt.expr.temp = $a obj
scoreboard players operation $i0 bolt.expr.temp += $b obj
execute store success score $2384k242hd495_70 bolt.expr.temp if score $i0 bolt.expr.temp matches 1..
execute unless score $2384k242hd495_70 bolt.expr.temp matches 0 run scoreboard players set $b obj 0
execute if score $2384k242hd495_70 bolt.expr.temp matches 0 run scoreboard players set $a obj 1
scoreboard players operation $2384k242hd495_75 bolt.expr.temp = $a obj
execute unless score $2384k242hd495_75 bolt.expr.temp matches 0 run say value exists
execute if score $2384k242hd495_75 bolt.expr.temp matches 0 run function test:main/nested_execute_0
scoreboard players operation $i0 bolt.expr.temp = $a obj
scoreboard players add $i0 bolt.expr.temp 5
execute store success score $2384k242hd495_81 bolt.expr.temp if score $i0 bolt.expr.temp matches 1..
execute unless score $2384k242hd495_81 bolt.expr.temp matches ..-1 unless score $2384k242hd495_81 bolt.expr.temp matches 1.. run scoreboard players operation $2384k242hd495_81 bolt.expr.temp = $b obj
scoreboard players operation $c obj = $2384k242hd495_81 bolt.expr.temp
scoreboard players operation $2384k242hd495_86 bolt.expr.temp = $a obj
execute unless score $2384k242hd495_86 bolt.expr.temp matches 0 run say it's a!
execute if score $2384k242hd495_86 bolt.expr.temp matches 0 run function test:main/nested_execute_1
execute store result score $i0 bolt.expr.temp run data get storage test:temp x 1
execute store success score $2384k242hd495_91 bolt.expr.temp if score $i0 bolt.expr.temp = $a obj
execute unless score $2384k242hd495_91 bolt.expr.temp matches 0 run say "a"
execute if score $2384k242hd495_91 bolt.expr.temp matches 0 run function test:main/nested_execute_2
