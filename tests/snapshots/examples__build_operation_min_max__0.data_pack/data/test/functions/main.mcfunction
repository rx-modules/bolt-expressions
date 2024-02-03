say 1
say 2
say 0
say 2
say (0, 1, 2)
say 3
say 2
say 0
say 2
say (0, 1, 3)
say {'x': -4}
say {'x': 4}
scoreboard players operation @s abc.main < $10 bolt.expr.const
scoreboard players operation @s abc.main > $20 bolt.expr.const
scoreboard players operation @s abc.main < $30 bolt.expr.const
scoreboard players operation @s abc.main > $40 bolt.expr.const
scoreboard players operation $a abc.main = $value abc.main
scoreboard players operation $a abc.main < $0 bolt.expr.const
scoreboard players operation $b abc.main = $value abc.main
scoreboard players operation $b abc.main > $0 bolt.expr.const
scoreboard players operation $c abc.main = $value abc.main
scoreboard players operation $c abc.main < $100 bolt.expr.const
scoreboard players operation $c abc.main > $0 bolt.expr.const
scoreboard players operation $d abc.main = $b abc.main
scoreboard players operation $d abc.main < $c abc.main
scoreboard players operation $d abc.main < $a abc.main
scoreboard players operation $e abc.main = $o abc.main
scoreboard players operation $e abc.main < $-1 bolt.expr.const
scoreboard players operation $e abc.main < $n abc.main
scoreboard players operation $e abc.main < $m abc.main
scoreboard players operation $f abc.main = $q abc.main
scoreboard players operation $f abc.main *= $3 bolt.expr.const
scoreboard players operation $i0 bolt.expr.temp = $r abc.main
scoreboard players remove $i0 bolt.expr.temp 1
scoreboard players operation $i0 bolt.expr.temp > $4 bolt.expr.const
scoreboard players operation $f abc.main > $i0 bolt.expr.temp
scoreboard players operation $f abc.main > $p abc.main
execute store result score $i0 bolt.expr.temp run data get storage example:main a 1
execute store result score $i1 bolt.expr.temp run data get storage example:main b 1
scoreboard players operation $i0 bolt.expr.temp < $i1 bolt.expr.temp
scoreboard players operation $i0 bolt.expr.temp < $a abc.main
execute store result storage example:main value int 1 run scoreboard players get $i0 bolt.expr.temp
execute store result score $result abc.main run data get storage example:main b 1
execute store result score $i0 bolt.expr.temp run data get storage example:main c 1
scoreboard players operation $result abc.main < $i0 bolt.expr.temp
execute store result score $i1 bolt.expr.temp run data get storage example:main a 1
scoreboard players operation $result abc.main < $i1 bolt.expr.temp
