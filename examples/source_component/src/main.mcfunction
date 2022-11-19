from bolt_expressions import Scoreboard, Data


temp = Scoreboard("obj.temp")

strg = Data.storage(example:main)
player = Data.entity("@s")
block = Data.block("~ ~ ~")

my_score = temp["@s"]

tellraw @a ["my score: ", my_score.component(bold=true)]

tellraw @a ["items: ", player.Inventory.component(color="green")]

click_event = {
    "action": "run_command",
    "value": "say i like bolt expressions"
}

tellraw @a ["message: ", strg.message.component(interpret=true, clickEvent=click_event)]


tellraw @a block.Text1

a = "hello world"
tellraw @a {"text":a}

tellraw @a {"text": "hi", "extra": [block.Items]}

msgg = [block.Text1, block.Text2, {text: "hi", extra:[block.Text3, {text:"nested"}]}]

tellraw @a msgg

view = {invalid:strg.value, whatever:temp["$a", "$b", "$c"]}
tellraw @a view


tellraw @a temp["$foo", "$bar", "$baz"]

tellraw @a [temp["$value"], block.Items[0], strg.message.component(interpret=true)]

