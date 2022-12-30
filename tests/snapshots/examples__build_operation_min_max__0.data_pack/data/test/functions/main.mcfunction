scoreboard players set $i0 bolt.expr.temp 10
scoreboard players operation $i0 bolt.expr.temp < @s abc.main
scoreboard players operation @s abc.main = $i0 bolt.expr.temp
scoreboard players set $i0 bolt.expr.temp 20
scoreboard players operation $i0 bolt.expr.temp > @s abc.main
scoreboard players operation @s abc.main = $i0 bolt.expr.temp
scoreboard players set $i0 bolt.expr.temp 30
scoreboard players operation $i0 bolt.expr.temp < @s abc.main
scoreboard players operation @s abc.main = $i0 bolt.expr.temp
scoreboard players set $i0 bolt.expr.temp 40
scoreboard players operation $i0 bolt.expr.temp > @s abc.main
scoreboard players operation @s abc.main = $i0 bolt.expr.temp
scoreboard players set $a abc.main 0
scoreboard players operation $a abc.main < $value abc.main
scoreboard players set $b abc.main 0
scoreboard players operation $b abc.main > $value abc.main
scoreboard players set $i0 bolt.expr.temp 100
scoreboard players operation $i0 bolt.expr.temp < $value abc.main
scoreboard players set $c abc.main 0
scoreboard players operation $c abc.main > $i0 bolt.expr.temp
scoreboard players operation $d abc.main = $c abc.main
scoreboard players operation $d abc.main < $b abc.main
scoreboard players operation $d abc.main < $a abc.main
scoreboard players set $e abc.main -1
scoreboard players operation $e abc.main < $o abc.main
scoreboard players operation $e abc.main < $n abc.main
scoreboard players operation $e abc.main < $m abc.main
scoreboard players operation $i0 bolt.expr.temp = $r abc.main
scoreboard players remove $i0 bolt.expr.temp 1
scoreboard players set $f abc.main 4
scoreboard players operation $f abc.main > $i0 bolt.expr.temp
scoreboard players set $i2 bolt.expr.temp 3
scoreboard players operation $i2 bolt.expr.temp *= $q abc.main
scoreboard players operation $f abc.main > $i2 bolt.expr.temp
scoreboard players operation $f abc.main > $p abc.main
