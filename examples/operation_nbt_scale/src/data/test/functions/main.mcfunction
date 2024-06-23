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


TICKS_PER_SECOND = 20
TICKS_PER_MINUTE = TICKS_PER_SECOND * 60
TICKS_PER_HOUR = TICKS_PER_MINUTE * 60

temp.hours = (obj["ticks_since_death"] - temp.death_gametime) / TICKS_PER_HOUR

obj["ticks_since_death"] = obj["ticks_since_death"] % TICKS_PER_MINUTE
temp.minutes = obj["ticks_since_death"] / TICKS_PER_MINUTE

obj["ticks_since_death"] = obj["ticks_since_death"] % TICKS_PER_SECOND
temp.seconds = obj["ticks_since_death"] / TICKS_PER_SECOND