say ("storage example:main ", list[test:main.Item], <class 'test:main.ExtendedDataSource'>)
say ("storage example:main [0]", <class 'test:main.Item'>, <class 'test:main.ExtendedDataSource'>)
say ("storage example:main [0].id", <class 'nbtlib.tag.String'>, <class 'test:main.ExtendedDataSource'>)
say ("storage example:main [0].Count", <class 'nbtlib.tag.Byte'>, <class 'test:main.ExtendedDataSource'>)
say ("storage example:main [0].tag", <class 'test:main.ItemTag'>, <class 'test:main.ExtendedDataSource'>)
say ("storage example:main [0].tag.Items", list[test:main.Item], <class 'test:main.ExtendedDataSource'>)
scoreboard players operation $a obj.temp = $value obj.temp
execute store result score $i0 bolt.expr.temp run data get storage example:main a 1
scoreboard players operation $a obj.temp -= $i0 bolt.expr.temp
execute store result storage example:main a byte 1 run scoreboard players get $a obj.temp
execute if data storage example:main {a: 0b} run say It's 0!
execute unless data storage example:main {a: 0b} run say It's not 0...
