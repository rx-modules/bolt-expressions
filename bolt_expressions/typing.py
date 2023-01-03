from types import GenericAlias, UnionType

from nbtlib import Base, Compound, Float, Int, List, String  # type: ignore

from .literals import convert_tag

from typing import Any, Union, _UnionGenericAlias, get_args  # type: ignore isort: skip

__all__ = [
    "is_type",
    "convert_type",
]


def is_type(value: dict[str, Any] | type | Any) -> bool:
    if isinstance(value, dict):
        return any(is_type(v) for v in value.values())

    return value is Any or isinstance(
        value, (type, UnionType, _UnionGenericAlias, GenericAlias)
    )


def convert_type(value: type | dict[str, Any] | Any) -> Any:
    if isinstance(value, dict):
        return convert_tag({key: convert_type(v) for key, v in value.items()})

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
