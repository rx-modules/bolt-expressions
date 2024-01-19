from functools import partial
from beet import Context
from bolt import Runtime

from .node import Expression
from .operations import wrapped_min, wrapped_max
from .api import Scoreboard, Data

__all__ = [
    "beet_default",
]


def bolt_expressions(ctx: Context):
    expr = ctx.inject(Expression)
    ctx.inject(Scoreboard)
    ctx.inject(Data)

    runtime = ctx.inject(Runtime)

    runtime.expose(
        "min", partial(wrapped_min, runtime.globals.get("min", min))
    )
    runtime.expose(
        "max", partial(wrapped_max, runtime.globals.get("max", max))
    )

    if not expr.opts.disable_commands:
        ctx.require("bolt_expressions.contrib.commands")

    yield

    expr.generate_init()


beet_default = bolt_expressions
