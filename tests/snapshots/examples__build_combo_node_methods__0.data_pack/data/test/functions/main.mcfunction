scoreboard players set #test abc.main 0
scoreboard players reset #test abc.main
scoreboard players enable #value abc.main
scoreboard players reset #value abc.main
data modify storage demo:temp value set value 10
data remove storage demo:temp value
data remove storage demo:temp path.to.list[0]
data remove storage demo:temp items[{id: "minecraft:diamond"}]
data remove storage demo:temp value{active: 1b}
data remove storage demo:temp inventory[0].tag.Unbreakable
say -----
data modify storage demo:temp inventory append value 1
data modify storage demo:temp inventory append value 0
execute store result storage demo:temp inventory[-1] int 1 run scoreboard players get #val abc.main
data modify storage demo:temp inventory append from storage demo:temp item
execute store result score $i0 bolt.expr.temp run data get storage demo:temp item 1
scoreboard players operation $i0 bolt.expr.temp += #val abc.main
data modify storage demo:temp inventory append value 0
execute store result storage demo:temp inventory[-1] int 1 run scoreboard players get $i0 bolt.expr.temp
say -----
data modify storage demo:temp inventory prepend value 1
data modify storage demo:temp inventory prepend value 0
execute store result storage demo:temp inventory[0] int 1 run scoreboard players get #val abc.main
data modify storage demo:temp inventory prepend from storage demo:temp item
execute store result score $i0 bolt.expr.temp run data get storage demo:temp item 1
scoreboard players operation $i0 bolt.expr.temp += #val abc.main
data modify storage demo:temp inventory prepend value 0
execute store result storage demo:temp inventory[0] int 1 run scoreboard players get $i0 bolt.expr.temp
say -----
data modify storage demo:temp inventory insert 2 value 1
data modify storage demo:temp inventory insert 1 value 0
execute store result storage demo:temp inventory[1] int 1 run scoreboard players get #val abc.main
data modify storage demo:temp inventory insert 3 from storage demo:temp item
execute store result score $i0 bolt.expr.temp run data get storage demo:temp item 1
scoreboard players operation $i0 bolt.expr.temp += #val abc.main
data modify storage demo:temp inventory insert 5 value 0
execute store result storage demo:temp inventory[5] int 1 run scoreboard players get $i0 bolt.expr.temp
say -----
data modify storage demo:temp inventory merge value {}
data modify storage demo:temp item merge from storage demo:temp other
data modify storage demo:temp item merge value 0
data merge storage demo:temp {installed: 1b}
