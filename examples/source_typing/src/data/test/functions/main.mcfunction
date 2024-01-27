from nbtlib import Path, Byte, Short, Int, Long, Float, Double, ByteArray, IntArray, LongArray, List, Compound, String
from typing import TypedDict, Any
from bolt_expressions import Data
from bolt_expressions.utils import assert_exception


storage = Data.storage(name:path)

say (storage[bool].writetype)
say (storage[Byte].writetype)

say (storage[Short].writetype)

say (storage[int].writetype)
say (storage[Int].writetype)

say (storage[Long].writetype)

say (storage[float].writetype)
say (storage[Float].writetype)

say (storage[Double].writetype)

say (storage[dict].writetype)
say (storage[dict[str, Any]].writetype)
say (storage[Compound].writetype)
say (storage[Compound[Any]].writetype)

say (storage[list].writetype)
say (storage[List].writetype)
say (storage[list[Any]].writetype)
say (storage[List[String]].writetype)
say (storage[List[str]].writetype)
say (storage[list[String]].writetype)
say (storage[list[str]].writetype)

say (storage[ByteArray].writetype)
say (storage[IntArray].writetype)
say (storage[LongArray].writetype)

say (storage[str].writetype)
say (storage[String].writetype)

say (storage[str | None].writetype)
say (storage[str | int | None].writetype)



class ItemTag(TypedDict):
    CustomModelData: int
    Items: list["Item"]

class Item(TypedDict):
    id: str
    Count: Byte
    tag: ItemTag


temp = Data.storage(demo:temp)

say (type(temp))
say (type(temp.foo[int]))
say (type(temp.foo[bool]))
say (type(temp.foo[dict[str, Any]]))
say (type(temp.foo[Item]))

foo = temp.foo[list[Item]]

say (type(foo[list[Item]]))
say (type(foo[list[Item]][0]))
say (foo[{id:"minecraft:string"}].writetype)        



item = storage.item[Item]
say (item, item.writetype)
say (item.id, item.id.writetype)
say (item.Count, item.Count.writetype)
say (item.tag, item.tag.writetype)
say (item.tag.a, item.tag.a.writetype)
say (item.tag({}), item.tag({}).writetype)
say (item.tag.Items, item.tag.Items.writetype)
say (item.tag.Items[1], item.tag.Items[1].writetype)
say (item.tag.Items[1].id, item.tag.Items[1].id.writetype)
say (item.tag.Items[1].tag.CustomModelData, item.tag.Items[1].tag.CustomModelData.writetype)

item.tag.Items[0].Count = storage.value

say (item, type(item))
say (item.id, type(item.id))
say (item.idd, type(item.idd))
say (item.Count, type(item.Count))
say (item.tag, type(item.tag))
say (item.tag.Items, type(item.tag.Items))
say (item.tag.Items[0], type(item.tag.Items[0]))


string = storage.msg[str]

with assert_exception(TypeError):
    string.value
with assert_exception(TypeError):
    string[0]
with assert_exception(TypeError):
    string({})


num = storage.msg[int]

num + 1
with assert_exception(TypeError):
    num.value
with assert_exception(TypeError):
    num[0]
with assert_exception(TypeError):
    num({})


list_nbt = storage.msg[list]

list_nbt[0]
with assert_exception(TypeError):
    list_nbt.value
with assert_exception(TypeError):
    list_nbt({})
with assert_exception(TypeError):
    list_nbt + 1


item.id
item.idd
item({})
with assert_exception(TypeError):
    item[0]
with assert_exception(TypeError):
    item + 1