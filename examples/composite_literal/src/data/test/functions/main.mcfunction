from nbtlib import Path, Byte, Short, Int, Long, Float, Double, ByteArray, IntArray, LongArray, List, Compound, String
from typing import TypedDict, Any
from bolt_expressions import Scoreboard, Data
from bolt_expressions.typing import infer_type
from bolt_expressions.utils import assert_exception

obj = Scoreboard("obj.main")
storage = Data.storage(name:path)


class Version(TypedDict):
    major: Short
    minor: Short
    patch: Short

class PackConfig(TypedDict):
    version: Version
    data: dict[str, Any]
    timers: list[Double] | None


storage.config[PackConfig] = {
    version: {
        major: obj["$major"],
        minor: obj["$minor"],
        patch: obj["$patch"],
    },
    data: {
        x: Data.cast(storage.player_x * 100, Double),
        y: Data.cast(obj["$y"] / 100, Double),
        z: Data.cast(obj["$z"] / 100, Double),
        messages: [{"extra": [storage.name, ": ", storage.text, "."]}, {"text": storage.msg_text[str]}],
    },
}

storage.pos = [
    Data.cast(obj["$x"] / 100, Double),
    Data.cast(obj["$y"] / 100, Double),
    Data.cast(obj["$z"] / 100, Double),
]

storage.vec1 = [obj["$a"], obj["$b"]]

storage.vec2 = Data.cast([obj["$a"], obj["$b"], obj["$c"]], list[Long])

storage.vec3 = [obj["$a"], obj["$b"], Byte(5)]

storage.vec4 = Data.cast([obj["$a"], obj["$b"], obj["$c"]], ByteArray)


with var Data.cast({x: obj["$x"], y: obj["$y"], z: obj["$z"]}):
    $tp @s $(x) $(y) $(z)


say ---


storage.config = {
    pack_name: storage.pack_name[str],
    version: Data.cast([obj["$major"], obj["$minor"], obj["$patch"]], list[Short]),
    data: {
        flag0: Data.cast(obj["$flag0"], Byte),
        flag1: Data.cast(obj["$flag1"], Byte)
    }
}

class Item(TypedDict):
    id: str
    Count: Byte
    tag: dict[str, Any] | None

items = storage.items[list[Item]]
items.append({id: storage.selected_item, Count: obj["$count"]})


with var Data.cast({x: obj["$x"], y: obj["$y"], z: obj["$z"]}):
    $tp @s $(x) $(y) $(z)