from dataclasses import dataclass
from typing import Any, ClassVar, Iterable

from nbtlib import Base, Byte, Compound, Double, Float, Int, List, Long, Short, String

from .optimizer import IrLiteral

from .node import ExpressionNode

__all__ = [
    "Literal",
    "literal_types",
    "convert_tag",
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


def convert_tag(value):
    match value:
        case Base():
            return value
        case list():
            return List([convert_tag(x) for x in value])
        case dict():
            return Compound({key: convert_tag(value) for key, value in value.items()})
        case bool():
            return Byte(value)
        case int():
            return Int(value)
        case float():
            return Float(value)
        case str():
            return String(value)
        case _:
            return value


@dataclass(unsafe_hash=True, order=False)
class Literal(ExpressionNode):
    value: Any

    @classmethod
    def create(cls, value: Base):
        tag = convert_tag(value)
        if tag is None:
            raise ValueError(f'Invalid expression node of type {type(value)} "{value}"')
        return super().create(tag)

    def __str__(self):
        return self.value.snbt()

    def __repr__(self):
        return self.value.snbt()

    def unroll(self):
        return (), IrLiteral(value=self.value)
