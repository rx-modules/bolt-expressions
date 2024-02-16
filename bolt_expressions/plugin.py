from dataclasses import dataclass, field
from functools import partial
from typing import Any
from beet import Context
from bolt import Runtime
from bolt.utils import internal
from mecha import Mecha

import bolt_expressions as bolt_expressions_module
from .ast import (
    ConstantScoreChecker,
    ObjectiveChecker,
    RunExecuteTransformer,
    SourceJsonConverter,
)
from .node import Expression
from .expose import wrapped_min, wrapped_max
from .api import Scoreboard, Data

__all__ = [
    "beet_default",
    "bolt_expressions",
]


def bolt_expressions(ctx: Context):
    ctx.require("bolt_control_flow")

    expr = ctx.inject(Expression)
    scoreboard = ctx.inject(Scoreboard)
    data = ctx.inject(Data)

    mc = ctx.inject(Mecha)
    mc.transform.extend(RunExecuteTransformer())
    mc.check.extend(
        ConstantScoreChecker(
            objective=expr.opts.const_objective, callback=scoreboard.add_constant
        ),
        ObjectiveChecker(
            whitelist=scoreboard.objectives,
            callback=scoreboard.add_objective,
        ),
    )

    runtime = ctx.inject(Runtime)

    api = {
        "Expression": expr,
        "Scoreboard": scoreboard,
        "Data": data,
    }
    handler = module_attribute_handler(
        ctx, runtime.helpers["get_attribute_handler"], api
    )
    json_converter = SourceJsonConverter(runtime.helpers["interpolate_json"])
    runtime.helpers["get_attribute_handler"] = handler
    runtime.helpers["interpolate_json"] = json_converter

    runtime.expose("min", partial(wrapped_min, runtime.globals.get("min", min)))
    runtime.expose("max", partial(wrapped_max, runtime.globals.get("max", max)))

    if not expr.opts.disable_commands:
        ctx.require("bolt_expressions.contrib.commands")

    yield

    expr.generate_init()


beet_default = bolt_expressions


def module_attribute_handler(
    ctx: Context, previus_handler: Any, attributes: dict[str, Any]
):
    def handler(obj: Any):
        if obj is bolt_expressions_module:
            return ExtendedAttributeHandler(obj, previus_handler(obj), ctx, attributes)

        return previus_handler(obj)

    return handler


@dataclass
class ExtendedAttributeHandler:
    obj: Any
    handler: Any
    ctx: Context

    attributes: dict[str, Any] = field(default_factory=dict)

    @internal
    def __getitem__(self, attr: str) -> Any:
        if attr in self.attributes:
            return self.attributes[attr]

        return self.handler[attr]

    @internal
    def __setitem__(self, attr: str, value: Any):
        self.handler[attr] = value

    @internal
    def __delitem__(self, attr: str):
        del self.handler[attr]
