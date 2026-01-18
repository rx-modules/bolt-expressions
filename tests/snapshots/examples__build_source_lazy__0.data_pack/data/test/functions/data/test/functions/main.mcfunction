scoreboard players operation $5ws9foxn8m17m_2 bolt.expr.temp = $a obj.temp
scoreboard players operation $5ws9foxn8m17m_2 bolt.expr.temp += $b obj.temp
scoreboard players operation $5ws9foxn8m17m_2 bolt.expr.temp /= $2 bolt.expr.const
say $5ws9foxn8m17m_2 bolt.expr.temp
say $5ws9foxn8m17m_5 bolt.expr.temp
scoreboard players operation $result obj.temp = $a obj.temp
scoreboard players operation $result obj.temp += $b obj.temp
scoreboard players operation $result obj.temp /= $2 bolt.expr.const
scoreboard players operation $result obj.temp %= $d obj.temp
scoreboard players operation $result obj.temp *= $100 bolt.expr.const
scoreboard players operation $x obj.temp = $a obj.temp
scoreboard players operation $x obj.temp += $b obj.temp
scoreboard players operation $x obj.temp /= $2 bolt.expr.const
say <class 'bolt_expressions.sources.ScoreSource'>
say True
scoreboard players operation $t obj.temp = $a obj.temp
scoreboard players operation $t obj.temp += $b obj.temp
scoreboard players operation $t obj.temp /= $2 bolt.expr.const
scoreboard players operation $u obj.temp = $5ws9foxn8m17m_2 bolt.expr.temp
scoreboard players operation $v obj.temp = $5ws9foxn8m17m_2 bolt.expr.temp
scoreboard players operation $w obj.temp = $5ws9foxn8m17m_2 bolt.expr.temp
say False
data modify storage bolt.expr:temp 5ws9foxn8m17m_18 set from storage demo:temp default_fields
data modify storage bolt.expr:temp 5ws9foxn8m17m_18 merge from storage demo:temp current_fields
data modify storage bolt.expr:temp 5ws9foxn8m17m_18.color[0] set value 127b
data modify storage demo:temp output_color set from storage bolt.expr:temp 5ws9foxn8m17m_18.color
data modify storage bolt.expr:temp 5ws9foxn8m17m_21 set from storage demo:temp chest1
data modify storage bolt.expr:temp 5ws9foxn8m17m_21 merge from storage demo:temp chest2
data modify storage bolt.expr:temp 5ws9foxn8m17m_21 merge from storage demo:temp chest3
data modify storage bolt.expr:temp 5ws9foxn8m17m_21 merge value {}
data modify storage bolt.expr:temp 5ws9foxn8m17m_21 merge value {}
scoreboard players operation $5ws9foxn8m17m_24 bolt.expr.temp = $a obj.temp
scoreboard players add $5ws9foxn8m17m_24 bolt.expr.temp 2
scoreboard players operation $5ws9foxn8m17m_24 bolt.expr.temp -= $b obj.temp
scoreboard players operation @s obj.temp = $a obj.temp
scoreboard players add @s obj.temp 2
scoreboard players operation @s obj.temp -= $b obj.temp
scoreboard players enable $5ws9foxn8m17m_24 bolt.expr.temp
scoreboard players operation $a1 obj.temp = $5ws9foxn8m17m_24 bolt.expr.temp
scoreboard players operation $a2 obj.temp = $5ws9foxn8m17m_24 bolt.expr.temp
scoreboard players operation $5ws9foxn8m17m_27 bolt.expr.temp = @s obj.temp
scoreboard players operation $5ws9foxn8m17m_27 bolt.expr.temp *= $5 bolt.expr.const
tellraw @a {score: {name: "$5ws9foxn8m17m_27", objective: "bolt.expr.temp"}}
scoreboard players operation $5ws9foxn8m17m_30 bolt.expr.temp = $v obj.temp
scoreboard players operation $5ws9foxn8m17m_30 bolt.expr.temp *= $5 bolt.expr.const
scoreboard players operation $5ws9foxn8m17m_30 bolt.expr.temp /= $w obj.temp
scoreboard players set $v obj.temp 0
execute if score $5ws9foxn8m17m_30 bolt.expr.temp matches 1.. run say Hello 
function test:data/test/functions/main/sum
function test:data/test/functions/main/sum
