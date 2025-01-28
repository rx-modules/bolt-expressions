scoreboard players operation __2384k242hd495_0 bolt.expr.temp = @s abc.obj
scoreboard players operation __2384k242hd495_0 bolt.expr.temp %= #5 bolt.expr.const
execute if score __2384k242hd495_0 bolt.expr.temp matches 0
scoreboard players operation @s abc.obj = #value abc.obj
scoreboard players operation @s abc.obj *= #2 bolt.expr.const
scoreboard players add @s abc.obj 1
scoreboard players operation __i0 bolt.expr.temp = #denom abc.obj
scoreboard players operation __i0 bolt.expr.temp *= #5 bolt.expr.const
scoreboard players operation @s abc.obj /= __i0 bolt.expr.temp
scoreboard players operation @s abc.obj = #value abc.obj
scoreboard players operation @s abc.obj *= #3 bolt.expr.const
scoreboard players operation @s abc.obj *= #4 bolt.expr.const
scoreboard players operation @s abc.obj *= #6 bolt.expr.const
scoreboard players operation @s abc.obj *= #7 bolt.expr.const
scoreboard players operation @s abc.obj *= #8 bolt.expr.const
scoreboard players operation @s abc.obj = #value abc.obj
scoreboard players operation @s abc.obj *= #-5 bolt.expr.const
scoreboard players operation __i0 bolt.expr.temp = #value abc.obj
scoreboard players operation __i0 bolt.expr.temp *= #123 bolt.expr.const
scoreboard players add __i0 bolt.expr.temp 10
scoreboard players operation @s abc.obj += __i0 bolt.expr.temp
scoreboard players operation __i0 bolt.expr.temp = #value abc.obj
scoreboard players operation __i0 bolt.expr.temp *= #0 bolt.expr.const
scoreboard players add __i0 bolt.expr.temp 50
scoreboard players operation @s abc.obj %= __i0 bolt.expr.temp
