from dataclasses import dataclass
from typing import ClassVar

from nbtlib import Base, Byte, Compound, Double, Float, Int, List, Long, Short, String

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
    if isinstance(value, Base):
        return value
    t = type(value)
    if t is list:
        return List([convert_tag(x) for x in value])
    if t is dict:
        return Compound({key: convert_tag(value) for key, value in value.items()})
    if t is bool:
        return Byte(value)
    if t is int:
        return Int(value)
    if t is float:
        return Float(value)
    if t is str:
        return String(value)


@dataclass(unsafe_hash=True, order=False)
class Literal(ExpressionNode):
    value: Base

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
