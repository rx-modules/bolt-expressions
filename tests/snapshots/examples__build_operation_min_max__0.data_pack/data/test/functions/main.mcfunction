scoreboard players operation @s abc.main < $10 bolt.expr.const
scoreboard players operation @s abc.main > $20 bolt.expr.const
scoreboard players set $i33 bolt.expr.temp 30
scoreboard players operation $i33 bolt.expr.temp < @s abc.main
scoreboard players operation @s abc.main = $i33 bolt.expr.temp
scoreboard players set $i34 bolt.expr.temp 40
scoreboard players operation $i34 bolt.expr.temp > @s abc.main
scoreboard players operation @s abc.main = $i34 bolt.expr.temp
