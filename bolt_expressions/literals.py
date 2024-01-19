from dataclasses import dataclass, field
from typing import Any
from beet import Context

from nbtlib import Array, Byte, Compound, Double, Float, Int, List, Long, Short, String  # type: ignore
from beet.core.utils import required_field

from .optimizer import IrLiteral, NbtType
from .node import Expression, ExpressionNode
from .utils import type_name

__all__ = [
    "Literal",
    "literal_types",
    "convert_tag",
    "convert_node",
]

literal_types = {
    "byte": Byte,
    "short": Short,
    "int": Int,
    "long": Long,
    "float": Float,
    "double": Double,
    "compound": Compound,
    "list": List,
    "string": String,
}


def convert_tag(value: Any) -> NbtType | None:
    match value:
        case Byte() | Short() | Int() | Float() | Double() | String() | List() | Array() | Compound():
            return value
        case list():
            return List([convert_tag(x) for x in value])  # type: ignore
        case dict(dict_value):  # type: ignore
            return Compound({key: convert_tag(value) for key, value in value.items()})  # type: ignore
        case bool():
            return Byte(value)
        case int():
            return Int(value)
        case float():
            return Float(value)
        case str():
            return String(value)
        case _:
            return None


@dataclass(unsafe_hash=True, order=False)
class Literal(ExpressionNode):
    value: Any = required_field(repr=False)
    nbt: NbtType = field(init=False)

    def __post_init__(self):
        value = convert_tag(self.value)

        if value is None:
            raise ValueError(
                f'Invalid literal of type {type_name(value)} "{value}".'
            )

        self.nbt = value

    def __str__(self):
        return self.nbt.snbt() # type: ignore

    def unroll(self):
        return (), IrLiteral(value=self.nbt)


def convert_node(value: Any, ctx: Context | Expression) -> ExpressionNode:
    if isinstance(value, ExpressionNode):
        return value
    
    return Literal(value=value, ctx=ctx)
