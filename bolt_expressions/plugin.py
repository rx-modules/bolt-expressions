from beet import Context
from bolt_expressions import Scoreboard

def beet_default(ctx: Context):
    ctx.inject(Scoreboard)
