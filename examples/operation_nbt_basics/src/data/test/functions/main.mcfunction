from bolt_expressions import Scoreboard, Data
from nbtlib import Short, Double, List, Compound, Int

Objective = ctx.inject(Scoreboard)
Nbt = ctx.inject(Data)

obj = Objective("abc.main")

temp = Nbt.storage("demo:prefix/temp")

this_block = Nbt.block("~1 ~2 ~3")
origin_block = Nbt.block("0 0 0")
facing_block = Nbt.block("^ ^ ^5")

player = Nbt.entity("@s")
entity = Nbt.entity("@s")
rx = Nbt.entity("rx97")
thewii = Nbt.entity("TheWii")

function ./operations:
    obj["@s"] += player.Health
    obj["@s"] -= rx.SelectedItem.Count
    obj["@s"] *= thewii.SelectedItem.Damage
    obj["@s"] /= origin_block.RecordItem.data
    obj["@s"] %= this_block.Items[0]
    temp.foo = temp.bar
    temp.player += player.Health
    temp.player -= rx.SelectedItem.Count
    temp.player *= thewii.SelectedItem.Damage
    temp.player /= origin_block.RecordItem.data
    temp.player %= this_block.Items[0]
    this_block.Items[-1].Count += player.SelectedItem.Count 

    

function ./literals:
    player.Health = 10
    player.Health += 20
    rx.Health -= 30
    origin_block.data.ur_mom *= 40
    this_block.Items[0].Count /= 50
    thewii.Inventory['{Slot: -103b}'].tag.data.bolt %= 60
    player.Inventory[:].tag.string = "your mom"
    player.Inventory[:].tag.int = 10
    player.Inventory[:].tag.float = 10.0
    player.Inventory[:].tag.double = Double(10.0)
    player.Inventory[:].tag.list = []
    player.Inventory[:].tag.list = [1, 2, 3]
    player.Inventory[:].tag.list = [1, 2, 3] + [4, 5, 6]
    player.Inventory[:].tag.list = [{}, {}, {}]
    player.Inventory[:].tag.list = [{"bar": 2.5}, {"baz": false}]
    player.Inventory[:].tag.list = {}
    player.Inventory[:].tag.list = {"foo": 2, "baz": Short(-1)}