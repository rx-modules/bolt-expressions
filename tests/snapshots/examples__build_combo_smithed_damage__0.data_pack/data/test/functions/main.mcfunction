scoreboard players operation $i0 bolt.expr.temp = armor smithed.damage
scoreboard players operation $i0 bolt.expr.temp *= $10 bolt.expr.const
scoreboard players operation $i1 bolt.expr.temp = damage smithed.damage
scoreboard players operation $i1 bolt.expr.temp *= $400 bolt.expr.const
scoreboard players operation $i2 bolt.expr.temp = toughness smithed.damage
scoreboard players operation $i2 bolt.expr.temp *= $10 bolt.expr.const
scoreboard players add $i2 bolt.expr.temp 80
scoreboard players operation $i1 bolt.expr.temp /= $i2 bolt.expr.temp
scoreboard players operation $i0 bolt.expr.temp -= $i1 bolt.expr.temp
scoreboard players operation $i3 bolt.expr.temp = armor smithed.damage
scoreboard players operation $i3 bolt.expr.temp *= $10 bolt.expr.const
scoreboard players operation $i3 bolt.expr.temp /= $5 bolt.expr.const
scoreboard players operation $i0 bolt.expr.temp > $i3 bolt.expr.temp
scoreboard players operation $i0 bolt.expr.temp < $200 bolt.expr.const
scoreboard players set $i4 bolt.expr.temp 250
scoreboard players operation $i4 bolt.expr.temp -= $i0 bolt.expr.temp
scoreboard players operation $i4 bolt.expr.temp /= $25 bolt.expr.const
scoreboard players operation damage smithed.damage *= $i4 bolt.expr.temp
