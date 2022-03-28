from beet import Context, Function

from bolt_expressions import Expression, Scoreboard


def beet_default(ctx: Context):
    expression = ctx.inject(Expression)
    ctx.inject(Scoreboard)
    # ctx.require("mecha")

    yield

    expression.generate_init()
