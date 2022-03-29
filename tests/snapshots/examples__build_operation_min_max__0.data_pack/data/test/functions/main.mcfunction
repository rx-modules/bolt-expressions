scoreboard players operation @s abc.main < $10 bolt.expr.const
scoreboard players operation @s abc.main > $20 bolt.expr.const
scoreboard players set $i45 bolt.expr.temp 30
scoreboard players operation $i45 bolt.expr.temp < @s abc.main
scoreboard players operation @s abc.main = $i45 bolt.expr.temp
scoreboard players set $i46 bolt.expr.temp 40
scoreboard players operation $i46 bolt.expr.temp > @s abc.main
scoreboard players operation @s abc.main = $i46 bolt.expr.temp
