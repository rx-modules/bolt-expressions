execute store result score $2384k242hd495_94 bolt.expr.temp run data get storage test:temp x 1
execute if score $a obj = $2384k242hd495_94 bolt.expr.temp run return run say "b"
scoreboard players set $2384k242hd495_99 bolt.expr.temp 1
data modify storage bolt.expr:temp 2384k242hd495_100 set from storage test:temp x
execute if data storage test:temp x if data storage test:temp y store success score $2384k242hd495_99 bolt.expr.temp run data modify storage bolt.expr:temp 2384k242hd495_100 set from storage test:temp y
execute if score $2384k242hd495_99 bolt.expr.temp matches 0 run return run say "c"
execute if data storage test:temp {x: 5} run return run say "d"
data remove storage bolt.expr:temp 2384k242hd495_106
data modify storage bolt.expr:temp 2384k242hd495_106 set from storage test:temp x[0]
execute if data storage bolt.expr:temp {2384k242hd495_106: 5} run return run say "e"
execute if data storage test:temp {x: "hello"} run return run say "f"
scoreboard players set $2384k242hd495_113 bolt.expr.temp 1
data modify storage bolt.expr:temp 2384k242hd495_114 set from storage test:temp x
execute if data storage test:temp x store success score $2384k242hd495_113 bolt.expr.temp run data modify storage bolt.expr:temp 2384k242hd495_114 set value [1, 2, 3]
execute if score $2384k242hd495_113 bolt.expr.temp matches 0 run return run say "g"
scoreboard players set $2384k242hd495_119 bolt.expr.temp 1
data modify storage bolt.expr:temp 2384k242hd495_120 set from storage test:temp x
execute if data storage test:temp x store success score $2384k242hd495_119 bolt.expr.temp run data modify storage bolt.expr:temp 2384k242hd495_120 set value {}
execute if score $2384k242hd495_119 bolt.expr.temp matches 0 run say "h"
