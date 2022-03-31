from bolt_expressions import Expression, Scoreboard

merge function_tag minecraft:load {
    "values": [
        "test:load"
    ]
}

abc = Scoreboard("abc.main")

function ./load:
    if score #dependency load.status matches 1.. function ./install:
        say Installing pack...
        Expression.init()

abc["@s"] = (abc["#value"] * 2 + 1) / (abc["#denom"] * 5)
abc["@s"] = abc["#value"] * 3 * 4 * 6 * 7 * 8
abc["@s"] = abc["#value"] * -5
abc["@s"] += 10 + abc["#value"] * 123
abc["@s"] %= 50 + abc["#value"] * 0
