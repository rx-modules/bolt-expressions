say <class 'nbtlib.tag.Byte'>
say <class 'nbtlib.tag.Byte'>
say <class 'nbtlib.tag.Short'>
say <class 'nbtlib.tag.Int'>
say <class 'nbtlib.tag.Int'>
say <class 'nbtlib.tag.Long'>
say <class 'nbtlib.tag.Float'>
say <class 'nbtlib.tag.Float'>
say <class 'nbtlib.tag.Double'>
say dict[nbtlib.tag.String, typing.Any]
say dict[nbtlib.tag.String, typing.Any]
say dict[nbtlib.tag.String, typing.Any]
say dict[nbtlib.tag.String, typing.Any]
say list[typing.Any]
say list[typing.Any]
say list[typing.Any]
say list[nbtlib.tag.String]
say list[nbtlib.tag.String]
say list[nbtlib.tag.String]
say list[nbtlib.tag.String]
say <class 'nbtlib.tag.ByteArray'>
say <class 'nbtlib.tag.IntArray'>
say <class 'nbtlib.tag.LongArray'>
say <class 'nbtlib.tag.String'>
say <class 'nbtlib.tag.String'>
say typing.Optional[nbtlib.tag.String]
say typing.Union[nbtlib.tag.String, nbtlib.tag.Int, NoneType]
say <class 'bolt_expressions.sources.DataSource'>
say <class 'bolt_expressions.sources.DataSource'>
say <class 'bolt_expressions.sources.DataSource'>
say <class 'bolt_expressions.sources.DataSource'>
say <class 'bolt_expressions.sources.DataSource'>
say <class 'bolt_expressions.sources.DataSource'>
say <class 'bolt_expressions.sources.DataSource'>
say <class 'test:main.Item'>
say ("storage name:path item", <class 'test:main.Item'>)
say ("storage name:path item.id", <class 'nbtlib.tag.String'>)
say ("storage name:path item.Count", <class 'nbtlib.tag.Byte'>)
say ("storage name:path item.tag", <class 'test:main.ItemTag'>)
say ("storage name:path item.tag.a", typing.Any)
say ("storage name:path item.tag{}", <class 'test:main.ItemTag'>)
say ("storage name:path item.tag.Items", list[test:main.Item])
say ("storage name:path item.tag.Items[1]", <class 'test:main.Item'>)
say ("storage name:path item.tag.Items[1].id", <class 'nbtlib.tag.String'>)
say ("storage name:path item.tag.Items[1].tag.CustomModelData", <class 'nbtlib.tag.Int'>)
execute store result storage name:path item.tag.Items[0].Count byte 1 run data get storage name:path value 1
say ("storage name:path item", <class 'bolt_expressions.sources.DataSource'>)
say ("storage name:path item.id", <class 'bolt_expressions.sources.DataSource'>)
say ("storage name:path item.idd", <class 'bolt_expressions.sources.DataSource'>)
say ("storage name:path item.Count", <class 'bolt_expressions.sources.DataSource'>)
say ("storage name:path item.tag", <class 'bolt_expressions.sources.DataSource'>)
say ("storage name:path item.tag.Items", <class 'bolt_expressions.sources.DataSource'>)
say ("storage name:path item.tag.Items[0]", <class 'bolt_expressions.sources.DataSource'>)
data modify storage name:path value set value [0.0d, 1.0d, 3.0d, 1.0d, 127.0d]
data modify storage name:path value append value 3.0d
data modify storage name:path value prepend value 0.0d
data modify storage name:path value insert 4 value 13.0d
data modify storage bolt.expr:temp i0 set value {id: "bla", Count: 5, tag: {CustomModelData: 14.2f, Items: [{id: "stone", Count: 3}]}}
data modify storage bolt.expr:temp i0 merge from storage name:path other_item
execute store result storage name:path new_item int 1 run data modify storage bolt.expr:temp i0 merge value {tag: {Items: [{Count: 23}]}}
data modify storage name:path name set value "george"
data modify storage name:path flag set value 127b
data modify storage name:path flags set value [B; 1B, 2B, 3B, 127B]
data modify storage name:path arr append string storage name:path message 0 1
data modify storage name:path arr prepend string storage name:path message 1 -1
data modify storage name:path arr insert 0 string storage name:path message 3
data modify storage name:path arr merge string storage name:path message 0 3
data modify storage name:path message set string storage name:path message 1
data modify storage bolt.expr:temp 2384k242hd495_12 set string storage name:path message 5 10
tellraw @a {"nbt": "2384k242hd495_12", "storage": "bolt.expr:temp"}
data modify storage bolt.expr:temp 2384k242hd495_13 set string storage name:path message 0 1
say storage bolt.expr:temp 2384k242hd495_13
