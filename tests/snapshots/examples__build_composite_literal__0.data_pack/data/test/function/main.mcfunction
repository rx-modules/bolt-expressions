data modify storage name:path config set value {version: {major: 0s, minor: 0s, patch: 0s}, data: {x: 0.0d, y: 0.0d, z: 0.0d, messages: [{extra: ["", ": ", "", "."]}, {text: ""}]}}
execute store result storage name:path config.data.x double 100 run data get storage name:path player_x 1
execute store result storage name:path config.data.y double 0.01 run scoreboard players get $y obj.main
execute store result storage name:path config.data.z double 0.01 run scoreboard players get $z obj.main
execute store result storage name:path config.version.major short 1 run scoreboard players get $major obj.main
execute store result storage name:path config.version.minor short 1 run scoreboard players get $minor obj.main
execute store result storage name:path config.version.patch short 1 run scoreboard players get $patch obj.main
data modify storage name:path config.data.messages[0].extra[0] set from storage name:path name
data modify storage name:path config.data.messages[0].extra[2] set from storage name:path text
data modify storage name:path config.data.messages[1].text set from storage name:path msg_text
data modify storage name:path pos set value [0.0d, 0.0d, 0.0d]
execute store result storage name:path pos[0] double 0.01 run scoreboard players get $x obj.main
execute store result storage name:path pos[1] double 0.01 run scoreboard players get $y obj.main
execute store result storage name:path pos[2] double 0.01 run scoreboard players get $z obj.main
data modify storage name:path vec1 set value [0, 0]
execute store result storage name:path vec1[0] int 1 run scoreboard players get $a obj.main
execute store result storage name:path vec1[1] int 1 run scoreboard players get $b obj.main
data modify storage name:path vec2 set value [0L, 0L, 0L]
execute store result storage name:path vec2[0] long 1 run scoreboard players get $a obj.main
execute store result storage name:path vec2[1] long 1 run scoreboard players get $b obj.main
execute store result storage name:path vec2[2] long 1 run scoreboard players get $c obj.main
data modify storage name:path vec3 set value [0b, 0b, 5b]
execute store result storage name:path vec3[0] byte 1 run scoreboard players get $a obj.main
execute store result storage name:path vec3[1] byte 1 run scoreboard players get $b obj.main
data modify storage name:path vec4 set value [B; 0b, 0b, 0b]
execute store result storage name:path vec4[0] byte 1 run scoreboard players get $a obj.main
execute store result storage name:path vec4[1] byte 1 run scoreboard players get $b obj.main
execute store result storage name:path vec4[2] byte 1 run scoreboard players get $c obj.main
data modify storage bolt.expr:temp 2384k242hd495_34 set value {x: 0, y: 0, z: 0}
execute store result storage bolt.expr:temp 2384k242hd495_34.x int 1 run scoreboard players get $x obj.main
execute store result storage bolt.expr:temp 2384k242hd495_34.y int 1 run scoreboard players get $y obj.main
execute store result storage bolt.expr:temp 2384k242hd495_34.z int 1 run scoreboard players get $z obj.main
function test:main/nested_macro_0 with storage bolt.expr:temp 2384k242hd495_34
say ---
data modify storage name:path config set value {pack_name: "", version: [], data: {flag0: 0b, flag1: 0b}}
data modify storage name:path config.version set value [0s, 0s, 0s]
execute store result storage name:path config.version[0] short 1 run scoreboard players get $major obj.main
execute store result storage name:path config.version[1] short 1 run scoreboard players get $minor obj.main
execute store result storage name:path config.version[2] short 1 run scoreboard players get $patch obj.main
execute store result storage name:path config.data.flag0 byte 1 run scoreboard players get $flag0 obj.main
execute store result storage name:path config.data.flag1 byte 1 run scoreboard players get $flag1 obj.main
data modify storage name:path config.pack_name set from storage name:path pack_name
data modify storage bolt.expr:temp i0 set value {id: "", Count: 0b}
data modify storage bolt.expr:temp i0.id set from storage name:path selected_item
execute store result storage bolt.expr:temp i0.Count byte 1 run scoreboard players get $count obj.main
data modify storage name:path items append from storage bolt.expr:temp i0
data modify storage bolt.expr:temp 2384k242hd495_43 set value {x: 0, y: 0, z: 0}
execute store result storage bolt.expr:temp 2384k242hd495_43.x int 1 run scoreboard players get $x obj.main
execute store result storage bolt.expr:temp 2384k242hd495_43.y int 1 run scoreboard players get $y obj.main
execute store result storage bolt.expr:temp 2384k242hd495_43.z int 1 run scoreboard players get $z obj.main
function test:main/nested_macro_1 with storage bolt.expr:temp 2384k242hd495_43
