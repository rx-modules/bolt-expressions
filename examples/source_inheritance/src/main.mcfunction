from bolt_expressions import Scoreboard, Data, DataSource
from dataclasses import dataclass, replace
from contextlib import contextmanager
from typing import TypedDict
from nbtlib import Byte, Double

@dataclass(order=False, repr=False)
class ExtendedDataSource(DataSource):
    _inverted: bool = False

    @contextmanager
    def __branch__(self):
        if not self._inverted:
            if data var self:
                yield True
        else:
            unless data var self:
                yield True
    
    def __not__(self):
        return replace(self, _inverted=not self._inverted)

    def increment(self):
        self += 1


storage = ExtendedDataSource("storage", example:main, ctx=ctx)


class ItemTag(TypedDict):
    CustomModelData: int
    Items: list["Item"]

class Item(TypedDict):
    id: str
    Count: Byte
    tag: ItemTag

items = storage[list[Item]]

say (items, items.writetype, type(items))
say (items[0], items[0].writetype, type(items[0]))
say (items[0].id, items[0].id.writetype, type(items[0].id))
say (items[0].Count, items[0].Count.writetype, type(items[0].Count))
say (items[0].tag, items[0].tag.writetype, type(items[0].tag))
say (items[0].tag.Items, items[0].tag.Items.writetype, type(items[0].tag.Items))


temp = Scoreboard("obj.temp")

temp["$a"] = temp["$value"] - storage.a

storage.a[Byte] = temp["$a"]
if storage({a: Byte(0)}):
    say It's 0!
else:
    say It's not 0...