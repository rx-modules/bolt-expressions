# bolt-expressions

[![GitHub Actions](https://github.com/rx-modules/bolt-expressions/workflows/CI/badge.svg)](https://github.com/rx-modules/bolt-expressions/actions)
[![PyPI](https://img.shields.io/pypi/v/bolt-expressions.svg)](https://pypi.org/project/bolt-expressions/)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/bolt-expressions.svg)](https://pypi.org/project/bolt-expressions/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)
[![Discord](https://img.shields.io/discord/900530660677156924?color=7289DA&label=discord&logo=discord&logoColor=fff)](https://discord.gg/98MdSGMm8j)

> a `pandas`-esque API for creating expressions within bolt

## Introduction

Bolt is a scripting language which mixes both python and mcfunction. This package amplifies this language by adding an API for creating fluent expressions loosely based off of the `pandas` syntax. These expressions are use for simplifying large bits of scoreboard and storage operation allowing you to swiftly create complex operations with the ease of normal programming.

```py
from bolt_expressions import Scoreboard, Data

math = Scoreboard.objective("math")
storage = Data.storage(example:temp)

stack = storage.hotbar[0]

math["@s"] = stack.Count * math["$cost"] + math["$value"] - stack.tag.discount * 0.75
```
->
```mcfunction
execute store result score @s math run data get storage example:temp hotbar[0].Count 1
scoreboard players operation @s math *= $cost math
scoreboard players operation @s math += $value math
execute store result score $i1 bolt.expr.temp run data get storage example:temp hotbar[0].tag.discount 0.75
scoreboard players operation @s math -= $i1 bolt.expr.temp
```

## Installation

The package can be installed with `pip`. Note, you must have `beet`, `mecha` and `bolt` installed to use this package.

```bash
$ pip install bolt-expressions
```

## Getting started

This package is designed to be used within any `bolt` script (either a `.mcfunction` or `bolt` file) inside a `bolt` enabled project. 

```yaml
require:
    - bolt
    - bolt_expressions

pipeline:
    - mecha
```

Once you've required `bolt` and `bolt_expressions`, you are able to import the python package directly inside your bolt script.

```py
from bolt_expressions import Scoreboard, Data
```
Now you're free to use the API objects. Create objectives, block, storage and entity nbt sources to easily write expressions as simple or complex as you like to make it.

```py
math = Scoreboard.objective("math")
executor = Data.entity("@s")
block = Data.block("~ ~ ~")
storage = Data.storage(example:storage)

math["$value"] = math["$points"] + executor.Health*10 + block.Items[0].Count - storage.discount

storage.values.append(math["$value"])
```
->
```mcfunction
execute store result score $value math run data get entity @s Health 10
scoreboard players operation $value math += $points math
execute store result score $i1 bolt.expr.temp run data get block ~ ~ ~ Items[0].Count 1
scoreboard players operation $value math += $i1 bolt.expr.temp
execute store result score $i2 bolt.expr.temp run data get storage example:storage discount 1
scoreboard players operation $value math -= $i2 bolt.expr.temp
data modify storage example:storage values append value 0
execute store result storage example:storage values[-1] int 1 run scoreboard players get $value math
```

## Features

- Robust API supporting Scoreboards, Storage, Blocks, and Entities
- Provides an interface to manipulate large, complex mathematical expressions simplily
- Automatically initializes objectives and score constants
- Allows you to interopt custom variables with normal commands

Checkout some examples over at our [docs](https://rx-modules.github.io/bolt-expressions/)!

## Contributing

Contributions are welcome. Make sure to first open an issue discussing the problem or the new feature before creating a pull request. The project uses [`poetry`](https://python-poetry.org).

```bash
$ poetry install
```

You can run the tests with `poetry run pytest`.

```bash
$ poetry run pytest
```

The project must type-check with [`pyright`](https://github.com/microsoft/pyright). If you're using VSCode the [`pylance`](https://marketplace.visualstudio.com/items?itemName=ms-python.vscode-pylance) extension should report diagnostics automatically. You can also install the type-checker locally with `npm install` and run it from the command-line.

```bash
$ npm run watch
$ npm run check
```

The code follows the [`black`](https://github.com/psf/black) code style. Import statements are sorted with [`isort`](https://pycqa.github.io/isort/).

```bash
$ poetry run isort bolt_expressions examples tests
$ poetry run black bolt_expressions examples tests
$ poetry run black --check bolt_expressions examples tests
```

---

License - [MIT](https://github.com/rx-modules/bolt-expressions/blob/main/LICENSE)
