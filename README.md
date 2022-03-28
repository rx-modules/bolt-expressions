# bolt-expressions

[![GitHub Actions](https://github.com/rx-modules/bolt-expressions/workflows/CI/badge.svg)](https://github.com/rx-modules/bolt-expressions/actions)
[![PyPI](https://img.shields.io/pypi/v/FIXME.svg)](https://pypi.org/project/bolt-expressions/)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/FIXME.svg)](https://pypi.org/project/bolt-expressions/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)
[![Discord](https://img.shields.io/discord/900530660677156924?color=7289DA&label=discord&logo=discord&logoColor=fff)](https://discord.gg/98MdSGMm8j)

> a `pandas`-esque API for creating expressions within bolt

## Introduction

Bolt is a scripting language which mixes both python and mcfunction. This package amplifies this language by adding an API for creating fluent expressions losely based off of the `pandas` syntax. These expressions are use for simplifying large bits of scoreboard and storage operation allowing you to swiftly create complex operations with the ease of normal programming.

```py
from bolt_expressions import Scoreboard

Objective = ctx.inject(Scoreboard)
math = Objective("math")

math["@s"] = math["@r"] * 10 + math["@r"] + 100
```
->
```mcfunction
scoreboard players operations $i0 bolt.expressions.temp = @r math
scoreboard players operations $i0 bolt.expressions.temp *= #10 bolt.expressions.int
scoreboard players operations $i1 bolt.expressions.temp = @r math
scoreboard players add $i1 bolt.expressions.temp 100
scoreboard players operations $i0 bolt.expressions.temp += $i1 bolt.expressions.temp
scoreboard players operations @s math = $i0 bolt.expressions.temp
```

## Installation

The package can be installed with `pip`. Note, you must have both `beet` and `mecha` installed to use this package.

```bash
$ pip install bolt-expressions
```

## Getting started

This package is designed to be used within any `bolt` script (either a `.mcfunction` or `bolt` file) inside a `mecha.contrib.bolt` enabled project. Note, `bolt-expressions` is not a plugin (yet), so there's no need to `require` `bolt-expressions`.

```yaml
require:
    - mecha.contrib.bolt

pipeline:
    - mecha
```

Once you've enabled bolt, you are able to import the python package directly inside your bolt script.

```py
from bolt_expressions import Scoreboard, Storage
```

Any usage of the `bolt_expressions` package will require you to inject the current beet context into the API objects. Then, you can create an objective and start creating expressions.

```py
Objective = ctx.inject(Scoreboard)

math = Objective("math")
entity_id = Objective("entity_id")

math["@s"] += 10
```

## Features

The `Scoreboard` object provides a rich API for you to interact within your bolt landscape. Most numerical operations (such as `+`, `*`, `%`) will produce correct `scoreboard operation` commands for you to work with.

```
CONSTANT = 60 * 60 * 24
math["@s"] *= (entity_id["current_id"] / 200) + CONSTANT
```

You can also utilize local variables to simplify readability with longer operations. This is due to the unique `__rebind__` operator provided only in the `bolt` context which allows us provide custom behavior with the `=` operation. We also have defined helper functions such as `min` and `max`, alongside `sqrt` and `**` (for `pow`).

```py
dmg_obj = Objective("damage")
damage = dmg_obj["damage"]
toughness = dmg_obj["toughness"]
armor = dmg_obj["armor"]

atf = (10 * armor - (400 * damage / (80 + 10 * toughness)))  # local variable
maxxed = max((10 * armor) / 5, atf)                          # still local variable
damage = damage * (250 - (min(200, maxxed))) / 25            # calls __rebind__!
```

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
