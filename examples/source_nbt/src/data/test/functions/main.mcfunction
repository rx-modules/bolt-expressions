from nbtlib import Compound, Path, Byte, Short
from bolt_expressions import Data
from bolt_expressions.utils import assert_exception

temp = Data.storage(demo:temp)

function ./paths:
    #> Root
    say temp

    #> Selecting child tags by name
    say temp.item.tag.display.Name
    _item = temp.item
    display = _item.tag.display
    say display.Name
    say display.Lore

    #> Selecting child tags with weird names
    say temp.item.tag["(weird #_name@"].value

    #> Selecting element of array by index
    say temp.items[3]
    say temp.grid[0][2][1]
    next_item = temp.inv[0]
    ench = next_item.tag.Enchantments[1]
    say ench.id

    #> Selecting the root compound only if the matches the specified compound
    say temp('{has_stuff:1b,abc:"def"}')
    say temp('{has_stuff:1b,abc:"def"}').foo.bar
    matching = { has_stuff: Byte(1), abc: "def" }
    say temp(matching)
    matching["ghi"] = "jkl"
    say temp(matching)
    say temp(Path('{has_stuff:1b,abc:"def"}')).foo.bar

    #> Merging two paths
    to_unbreaking = Path('tag.Enchantments[{id:"minecraft:unbreaking"}]')
    say temp.items[0][to_unbreaking]
    say temp.chest.Items[-1][to_unbreaking].lvl


    #> Selecting tag only if it matches the specified compound
    say temp.item.tag('{Unbreakable:0, Damage:0s}')

    #> Specifying scale and number type
    say temp.value(scale=0.321)
    with assert_exception(TypeError):
        say temp.value(scale=45.2, type="double").preserved.scale
    say temp.scale.set(scale=0.5).until.set(scale=3).again

    #> Select all compound elements that match the specified compound
    say temp.foo["{test:1b}"]
    say temp.foo["{test:1b"]
    say temp.foo[{test: Byte(1)}]
    say temp.foo["{"]
    say temp.foo["{}"]
    say temp.foo["{its:compound}"]
    say temp.foo[" {becomes:named_tag}"]
    say temp.foo["{also:named_tag} "]

    val = temp.value
    data modify storage val._target val["{id: 0}"]._path set value 0
    data modify storage val._target val[{id: 0}]._path set value 0

    #> Selecting all elements in an array
    say temp.item.tag.Enchantments[]
    say temp.item.tag.Enchantments[:]
    say temp.items[].ids[].literal["all"].key
    say temp.items[:].ids[:].literal[":"].key

    #> Interpolating named tags
    colors = temp.config.colors
    for color in ("yellow", "blue", "red", "green"):
        say colors[color].hex_code