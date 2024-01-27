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
say <class 'bolt_expressions.sources.GenericDataSource'>
say <class 'bolt_expressions.sources.NumericDataSource'>
say <class 'bolt_expressions.sources.NumericDataSource'>
say <class 'bolt_expressions.sources.CompoundDataSource'>
say <class 'bolt_expressions.sources.CompoundDataSource'>
say <class 'bolt_expressions.sources.SequenceDataSource'>
say <class 'bolt_expressions.sources.CompoundDataSource'>
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
say ("storage name:path item", <class 'bolt_expressions.sources.CompoundDataSource'>)
say ("storage name:path item.id", <class 'bolt_expressions.sources.StringDataSource'>)
say ("storage name:path item.idd", <class 'bolt_expressions.sources.GenericDataSource'>)
say ("storage name:path item.Count", <class 'bolt_expressions.sources.NumericDataSource'>)
say ("storage name:path item.tag", <class 'bolt_expressions.sources.CompoundDataSource'>)
say ("storage name:path item.tag.Items", <class 'bolt_expressions.sources.SequenceDataSource'>)
say ("storage name:path item.tag.Items[0]", <class 'bolt_expressions.sources.CompoundDataSource'>)
data modify storage name:path value set value [0.0d, 1.0d, 3.0d, 1.0d, 127.0d]
data modify storage name:path value append value 3.0d
data modify storage name:path value prepend value 0.0d
data modify storage name:path value insert 4 value 13.0d
data modify storage name:path item set value {id: "bla", Count: 15b, tag: {CustomModelData: 14, Items: [{id: "stone", Count: 3b}]}}
data modify storage name:path new_item set from storage name:path item
data modify storage name:path new_item merge value {Count: 5b}
data modify storage name:path new_item merge from storage name:path other_item
data modify storage name:path new_item merge value {tag: {Items: [{Count: 23b}]}}
data modify storage name:path name set value "george"
data modify storage name:path flag set value 127b
data modify storage name:path flag set value 128
data modify storage name:path flags set value [B; 1B, 2B, 3B, 127B]
data modify storage name:path flags set value [1, 2, 3, 128]
