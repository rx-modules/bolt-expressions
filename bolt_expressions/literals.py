from dataclasses import dataclass, field
from typing import Any
from beet import Context

from beet.core.utils import required_field

from .optimizer import IrLiteral
from .typing import NbtValue, convert_tag
from .node import Expression, ExpressionNode, UnrollHelper
from .utils import type_name

__all__ = [
    "Literal",
    "convert_node",
]


@dataclass(unsafe_hash=True, order=False)
class Literal(ExpressionNode):
    value: Any = required_field(repr=False)
    nbt: NbtValue = field(init=False)

    def __post_init__(self):
        value = convert_tag(self.value)

        if value is None:
            raise ValueError(f'Invalid literal of type {type_name(value)} "{value}".')

        self.nbt = value

    def __str__(self):
        return self.nbt.snbt()  # type: ignore

    def unroll(self, helper: UnrollHelper):
        return (), IrLiteral(value=self.nbt)


def convert_node(value: Any, ctx: Context | Expression) -> ExpressionNode:
    if isinstance(value, ExpressionNode):
        return value

    return Literal(value=value, ctx=ctx)
