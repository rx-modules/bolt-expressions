from beet import Context, Function

import bolt_expressions as expr

__all__ = [
    "beet_default",
]


def beet_default(ctx: Context):
    expr.Expression = ctx.inject(expr._Expression)  # type: ignore
    expr.Scoreboard = ctx.inject(expr._Scoreboard)  # type: ignore
    expr.Data = ctx.inject(expr._Data)  # type: ignore

    yield

    expr.Expression.generate_init()
