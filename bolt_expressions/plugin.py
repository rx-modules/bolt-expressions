from beet import Context, Function

import bolt_expressions


def beet_default(ctx: Context):
    bolt_expressions.Expression = ctx.inject(bolt_expressions._Expression)  # type: ignore
    bolt_expressions.Scoreboard = ctx.inject(bolt_expressions._Scoreboard)  # type: ignore
    bolt_expressions.Data = ctx.inject(bolt_expressions._Data)              # type: ignore

    yield

    bolt_expressions.Expression.generate_init()
