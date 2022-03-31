from bolt_expressions import Scoreboard, Data
from nbtlib import Short, Double, List, Compound, Int

obj = Scoreboard("abc.main")
temp = Data.storage("demo:prefix/temp")
player = Data.entity("@s")

player.Inventory[:].tag.list = {
    "items": [
        { "id": "diamond", "Count": 12 },
        {
            "id": "diamond_axe",
            "Count": 12,
            "tag": {
                "CustomModelData": 1234
            }
        },
    ],
    "used": false,
    "things": {
        "abc": Double(123.456),
        "cdf": Short(123.456),
    }
}

def create_item(id, count=1, tag={}):
    return {
        "id": id,
        "Count": count,
        "tag": tag
    }

temp.items[0] = create_item("diamond")
temp.items[1] = create_item("iron_ingot", 15)

excalibur_display = { "Name": '{"text":"Excalibur","color":"gold"}' }
nbt = { "Damage": Short(0), "display": excalibur_display}
temp.items[2] = create_item("iron_sword", 1, nbt)

temp.foo = temp.bar
