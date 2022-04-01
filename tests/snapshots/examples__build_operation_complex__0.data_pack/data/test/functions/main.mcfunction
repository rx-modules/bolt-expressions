scoreboard players operation my_var abc.main = @s abc.main
scoreboard players operation my_var abc.main += @e abc.main
scoreboard players operation my_var abc.main *= $5 bolt.expr.const
scoreboard players operation $i1 bolt.expr.temp = @s abc.main
scoreboard players operation $i1 bolt.expr.temp *= $2 bolt.expr.const
scoreboard players operation my_var abc.main += $i1 bolt.expr.temp
