scoreboard players set $i12 bolt.expr.temp 10
scoreboard players operation $i12 bolt.expr.temp *= armor smithed.damage
scoreboard players operation $i12 bolt.expr.temp /= $5 bolt.expr.const
scoreboard players set $i14 bolt.expr.temp 10
scoreboard players operation $i14 bolt.expr.temp *= armor smithed.damage
scoreboard players set $i15 bolt.expr.temp 400
scoreboard players operation $i15 bolt.expr.temp *= damage smithed.damage
scoreboard players set $i16 bolt.expr.temp 10
scoreboard players operation $i16 bolt.expr.temp *= toughness smithed.damage
scoreboard players add $i16 bolt.expr.temp 80
scoreboard players operation $i15 bolt.expr.temp /= $i16 bolt.expr.temp
scoreboard players operation $i14 bolt.expr.temp -= $i15 bolt.expr.temp
scoreboard players operation $i12 bolt.expr.temp > $i14 bolt.expr.temp
scoreboard players set $i21 bolt.expr.temp 200
scoreboard players operation $i21 bolt.expr.temp < $i12 bolt.expr.temp
scoreboard players set $i22 bolt.expr.temp 250
scoreboard players operation $i22 bolt.expr.temp -= $i21 bolt.expr.temp
scoreboard players operation $i22 bolt.expr.temp /= $25 bolt.expr.const
scoreboard players operation damage smithed.damage *= $i22 bolt.expr.temp
