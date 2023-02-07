from beet import Context
from pydantic import BaseModel

__all__ = [
    "ExpressionOptions",
    "expression_options",
]


class ExpressionOptions(BaseModel):
    """Bolt Expressions Options"""

    temp_objective: str = "bolt.expr.temp"
    const_objective: str = "bolt.expr.const"
    temp_storage: str = "bolt.expr:temp"
    init_path: str = "init_expressions"
    objective_prefix: str = ""

    disable_commands: bool = False


def expression_options(ctx: Context):
    return ctx.validate("bolt_expressions", ExpressionOptions)
