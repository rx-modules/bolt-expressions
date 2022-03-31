from beet import Context, Function

from bolt_expressions import Data, Expression, Scoreboard


def beet_default(ctx: Context):
    expression = ctx.inject(Expression)
    ctx.inject(Scoreboard)
    ctx.inject(Data)

    yield

    expression.generate_init()
