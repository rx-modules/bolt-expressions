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
