from dataclasses import dataclass, field
from typing import Any, Iterable, cast
from beet import Context

from beet.core.utils import required_field

from .optimizer import CompositeNbtValue, IrCompositeLiteral, IrLiteral, IrOperation, IrSource
from .typing import NbtValue, convert_tag
from .node import Expression, ExpressionNode, UnrollHelper
from .utils import type_name

__all__ = [
    "Literal",
    "convert_node",
]


@dataclass(unsafe_hash=True, order=False)
class Literal(ExpressionNode):
    value: Any = required_field()
    nbt: NbtValue | None = field(init=False)

    def __post_init__(self):
        self.nbt = convert_tag(self.value)

    def unroll(self, helper: UnrollHelper) -> tuple[Iterable[IrOperation], Any]:
        operations: list[IrOperation] = []

        def nested_unroll(obj: Any) -> CompositeNbtValue | IrSource:
            if isinstance(obj, dict):
                obj = cast(dict[str, Any], obj)
                return {
                    key: nested_unroll(value)
                    for key, value in obj.items()
                }

            if isinstance(obj, list):
                obj = cast(list[Any], obj)
                return [nested_unroll(value) for value in obj]
            
            if isinstance(obj, ExpressionNode):
                ops, value = obj.unroll(helper)
                operations.extend(ops)
                
                return value.value if isinstance(value, IrLiteral) else value
        
            value = convert_tag(obj)

            if value is None:
                raise ValueError(f'Invalid literal of type {type_name(obj)} "{self.value}"')

            return value


        if self.nbt is None:
            value = nested_unroll(self.value)

            if isinstance(value, IrSource):
                return tuple(operations), value

            return tuple(operations), IrCompositeLiteral(value=value)

        return (), IrLiteral(value=self.nbt)


def convert_node(value: Any, ctx: Context | Expression) -> ExpressionNode:
    if isinstance(value, ExpressionNode):
        return value

    return Literal(value=value, ctx=ctx)
