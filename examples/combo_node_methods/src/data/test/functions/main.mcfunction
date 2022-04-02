from bolt_expressions import Scoreboard, Data

abc = Scoreboard("abc.main")
temp = Data.storage(demo:temp)

abc["#test"] = 0

abc["#test"].reset()

value = abc["#value"]
value.enable()
value.reset()

temp.value = 10

temp.remove("value")

temp.path.to.list.remove(0)

temp.items.remove('{id:"minecraft:diamond"}')

temp.value('{active: 1b}').remove()

temp.inventory[0].tag.Unbreakable.remove()

#temp.remove()
# raise an error, can't remove the root

say -----

temp.inventory.append(1)
temp.inventory.append(abc["#val"])
temp.inventory.append(temp.item)
temp.inventory.append(temp.item + abc["#val"])

say -----

temp.inventory.prepend(1)
temp.inventory.prepend(abc["#val"])
temp.inventory.prepend(temp.item)
temp.inventory.prepend(temp.item + abc["#val"])

say -----

temp.inventory.insert(2, 1)
temp.inventory.insert(1, abc["#val"])
temp.inventory.insert(3, temp.item)
temp.inventory.insert(5, temp.item + abc["#val"])

say -----

temp.inventory.merge({})
temp.item.merge(temp.other)
temp.item.merge(0)
temp.merge({"installed":true})
#temp.merge(temp.other) # error: Unsupported operation "mergeroot" for types: "data" and "data"
#temp.merge([]) # error: Expected nbt compound