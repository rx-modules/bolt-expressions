scoreboard players operation @s abc.main = #value abc.main
scoreboard players operation @s abc.main *= $2 bolt.expr.const
scoreboard players add @s abc.main 1
scoreboard players operation $i1 bolt.expr.temp = #denom abc.main
scoreboard players operation $i1 bolt.expr.temp *= $5 bolt.expr.const
scoreboard players operation @s abc.main /= $i1 bolt.expr.temp
scoreboard players operation @s abc.main = #value abc.main
scoreboard players operation @s abc.main *= $3 bolt.expr.const
scoreboard players operation @s abc.main *= $4 bolt.expr.const
scoreboard players operation @s abc.main *= $6 bolt.expr.const
scoreboard players operation @s abc.main *= $7 bolt.expr.const
scoreboard players operation @s abc.main *= $8 bolt.expr.const
scoreboard players operation @s abc.main = #value abc.main
scoreboard players operation @s abc.main *= $-5 bolt.expr.const
scoreboard players operation $i0 bolt.expr.temp = #value abc.main
scoreboard players operation $i0 bolt.expr.temp *= $123 bolt.expr.const
scoreboard players add $i0 bolt.expr.temp 10
scoreboard players operation @s abc.main += $i0 bolt.expr.temp
scoreboard players operation $i0 bolt.expr.temp = #value abc.main
scoreboard players operation $i0 bolt.expr.temp *= $0 bolt.expr.const
scoreboard players add $i0 bolt.expr.temp 50
scoreboard players operation @s abc.main %= $i0 bolt.expr.temp
