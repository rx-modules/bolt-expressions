from bolt_expressions import Scoreboard, Data


temp = Scoreboard("obj.temp")

strg = Data.storage(example:main)
player = Data.entity("@s")
block = Data.block("~ ~ ~")

data modify var strg.items set from var player.Inventory

data modify var block.Items append from var strg.items[]


diamonds_path = strg.items[{id:"minecraft:diamond"}]
count = temp["$count"]

if data var diamonds_path
    say There are diamonds!

store result score var count
    data get var diamonds_path.Count

if score var count matches 1:
    say "Only one diamond though :("

execute if score var temp["@s"] matches 10

if score var temp["$a"] = var temp["$b"]
    store result score var temp["$value"]
    scoreboard players add var temp["$a"] 1

if score var temp["$a"] = $b temp
if score $a temp = var temp["$b"]
if score $a temp = $b temp


store result score var temp["$test"] scoreboard players add var temp["$incr"] 1
store result score $test temp scoreboard players add $incr temp 1

test, incr = temp["$test", "$incr"]
store result score var test scoreboard players add var incr 1


def register_ids(*scores):
    for score in scores:
        store result score var score:
            temp["$incr"] += 1

register_ids(*temp["$red", "$green", "$blue"])


if score var ("$foo", "abc.test") matches 10
if data var ("entity", "@s", "{Health: 20.0f}")


macro add source1=bolt_expressions:source source2=bolt:expression:
    a, b = (source1.value, source2)
    a += b

add temp["$foo"] 10
add strg.value temp["$delta"] + 10