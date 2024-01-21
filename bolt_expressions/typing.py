from types import GenericAlias, UnionType
from typing import Any, Literal, Union, _UnionGenericAlias, get_args  # type: ignore isort: skip

from nbtlib import Base, Compound, Float, Int, List, String, Byte, Short, Long, Double, Array  # type: ignore


__all__ = [
    "is_type",
    "convert_type",
    "literal_types"
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


NBT_TYPE_STRING = ("byte", "short", "int", "long", "float", "double")
NbtTypeString = Literal["byte", "short", "int", "long", "float", "double"]

NbtValue = Byte | Short | Int | Float | Double | String | List | Array | Compound

def convert_tag(value: Any) -> NbtValue | None:
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


NbtType = Union[type, GenericAlias, UnionType, dict[str, "NbtType"]]


def is_type(value: dict[str, Any] | type | Any) -> bool:
    if isinstance(value, dict):
        return any(is_type(v) for v in value.values())

    return value is Any or isinstance(
        value, (type, UnionType, _UnionGenericAlias, GenericAlias)
    )


def convert_type(value: type | dict[str, Any] | Any) -> NbtType:
    if isinstance(value, dict):
        return {key: convert_type(v) for key, v in value.items()}

    if isinstance(value, (UnionType, _UnionGenericAlias)):
        args = get_args(value)
        converted = tuple(convert_type(arg) for arg in args)

        return Union[converted]  # type: ignore

    if isinstance(value, GenericAlias):
        args = get_args(value)

        converted = tuple(convert_type(arg) for arg in args)
        origin = convert_type(value.__origin__)

        if len(converted) == 1:
            converted = converted[0]

        return origin[converted]  # type: ignore

    if isinstance(value, type):
        if issubclass(value, Base):
            return value
        if issubclass(value, str):
            return String
        if issubclass(value, int):
            return Int
        if issubclass(value, float):
            return Float
        if issubclass(value, dict):
            return Compound
        if issubclass(value, list):
            return List

    return value