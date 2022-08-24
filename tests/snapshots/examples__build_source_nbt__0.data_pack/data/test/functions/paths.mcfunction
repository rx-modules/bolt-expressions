say storage demo:temp 
say storage demo:temp item.tag.display.Name
say storage demo:temp item.tag.display.Name
say storage demo:temp item.tag.display.Lore
say storage demo:temp item.tag."(weird #_name@".value
say storage demo:temp items[3]
say storage demo:temp grid[0][2][1]
say storage demo:temp inv[0].tag.Enchantments[1].id
say storage demo:temp {has_stuff: 1b, abc: "def"}
say storage demo:temp {has_stuff: 1b, abc: "def"}.foo.bar
say storage demo:temp {has_stuff: 1b, abc: "def"}
say storage demo:temp {has_stuff: 1b, abc: "def", ghi: "jkl"}
say storage demo:temp {has_stuff: 1b, abc: "def"}.foo.bar
say storage demo:temp items[0].tag.Enchantments[{id: "minecraft:unbreaking"}]
say storage demo:temp chest.Items[-1].tag.Enchantments[{id: "minecraft:unbreaking"}].lvl
say storage demo:temp item.tag{Unbreakable: 0, Damage: 0s}
say storage demo:temp value
say storage demo:temp value.preserved.scale
say storage demo:temp scale.set.until.set.again
say storage demo:temp foo[{test: 1b}]
say storage demo:temp foo."{test:1b"
say storage demo:temp foo[{test: 1b}]
say storage demo:temp foo."{"
say storage demo:temp foo[{}]
say storage demo:temp foo[{its: "compound"}]
say storage demo:temp foo." {becomes:named_tag}"
say storage demo:temp foo."{also:named_tag} "
data modify storage demo:temp value[{id: 0}] set value 0
data modify storage demo:temp value[{id: 0}] set value 0
say storage demo:temp item.tag.Enchantments[]
say storage demo:temp item.tag.Enchantments[]
say storage demo:temp items[].ids[].literal.all.key
say storage demo:temp items[].ids[].literal.":".key
say storage demo:temp config.colors.yellow.hex_code
say storage demo:temp config.colors.blue.hex_code
say storage demo:temp config.colors.red.hex_code
say storage demo:temp config.colors.green.hex_code
