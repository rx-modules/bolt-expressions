from bolt_expressions import Scoreboard, Data

obj = Scoreboard("obj")
temp = Data.storage("demo")
player = Data.entity("@s")

say # scaled data to data
temp.out = temp.value * 100

say # scaled score
temp.out = obj["$value"] / 100

say # scaled data
temp.out = temp.value / 100

say # get and set scaled data
temp.out = temp.value * 100 / 100

say # set scaled score
temp.out = (obj["$value"] + 1) * 50

say # set scaled score
temp.out = (obj["$value"] + 1) / 10

say # get scaled data
temp.out = (temp.value * 100) + 3

say # get scaled data, operate and set it back scaled down
temp.out = ((temp.value * 100) + 5) / 100

say # get scaled data
obj["#offset"] = (player.Motion[0] * 100) - obj["#x"]

say # append scaled score
temp.list.append(obj["$value"] / 100)

say # prepend scaled score
temp.list.prepend(obj["$value"] * 100)

say # insert scaled score
temp.list.insert(3, obj["$value"] * 100)