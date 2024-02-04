from contextlib import suppress
from dataclasses import dataclass, replace
from types import NoneType
from typing import Any, Iterable
from beet import Context

from mecha import Visitor, rule
from nbtlib import String, Compound, List, Array, List, NamedKey, ListIndex, OutOfRange  # type: ignore

from .typing import (
    NbtType,
    NbtValue,
    NumericNbtValue,
    access_type,
    convert_tag,
    is_array_type,
    is_compound_type,
    is_list_type,
    is_numeric_type,
    is_string_type,
    is_union,
    unwrap_optional_type,
)
from .optimizer import IrBinary, IrCast, IrData, IrLiteral, IrOperation


__all__ = [
    "TypeCaster",
]


def cast_dict(
    nbt_type: NbtType, value: dict[Any, Any], ctx: Context | None = None
) -> Compound | None:
    if not is_compound_type(nbt_type):
        return None

    result: dict[Any, Any] = {}

    for key, val in value.items():
        key_type = access_type(nbt_type, NamedKey(key), ctx)

        if not key_type:
            result[key] = val
            continue

        casted_val = cast_value(key_type, val, ctx)

        result[key] = casted_val if casted_val is not None else val

    return Compound(result)


def cast_list(
    nbt_type: NbtType, value: list[Any] | Array, ctx: Context | None = None
) -> List | Array | None:
    if is_list_type(nbt_type):
        cast_type = List
    elif is_array_type(nbt_type):
        cast_type = nbt_type
    else:
        return None

    result: list[Any] = []

    for i, element in enumerate(value):
        el_type = access_type(nbt_type, ListIndex(i))

        if el_type is None:
            return None

        element = cast_value(el_type, element, ctx)

        if element is None:
            return None

        result.append(element)

    return cast_type(result)


def cast_numeric(nbt_type: NbtType, value: int | float) -> NumericNbtValue | None:
    if not is_numeric_type(nbt_type):
        return None

    with suppress(OutOfRange):
        return nbt_type(value)


def cast_string(nbt_type: NbtType, value: str) -> String | None:
    if is_string_type(nbt_type):
        return String(value)

    return None


def cast_value(
    nbt_type: NbtType, value: NbtValue | Any, ctx: Context | None = None
) -> NbtValue | None:
    nbt_type = unwrap_optional_type(nbt_type)

    if nbt_type in (Any, None, NoneType) or is_union(nbt_type):
        return convert_tag(value)

    if isinstance(value, dict):
        return cast_dict(nbt_type, value, ctx)

    if isinstance(value, list):
        return cast_list(nbt_type, value, ctx)

    if isinstance(value, (int, float)):
        return cast_numeric(nbt_type, value)

    if isinstance(value, str):
        return cast_string(nbt_type, value)

    return convert_tag(value)


@dataclass(eq=False, kw_only=True)
class TypeCaster(Visitor):
    ctx: Context | None

    def __call__(self, nodes: Iterable[IrOperation]) -> Iterable[IrOperation]:  # type: ignore
        for node in nodes:
            yield self.invoke(node)

    @rule(IrOperation)
    def fallback(self, node: IrOperation) -> IrOperation:
        return node

    @rule(IrCast)
    def cast(self, node: IrCast) -> IrBinary:
        if not isinstance(node.left, IrData):
            return node
        if not isinstance(node.right, IrLiteral):
            return node

        casted_value = cast_value(node.cast_type, node.right.value, self.ctx)

        if casted_value is None:
            return node

        return replace(node, right=IrLiteral(value=casted_value))

    @rule(IrBinary, op="merge")
    def set(self, node: IrBinary) -> IrBinary:
        if not isinstance(node.left, IrData):
            return node
        if not isinstance(node.right, IrLiteral):
            return node

        casted_value = cast_value(node.left.nbt_type, node.right.value, self.ctx)

        if casted_value is None:
            return node

        return replace(node, right=IrLiteral(value=casted_value))

    @rule(IrBinary, op="insert")
    @rule(IrBinary, op="append")
    @rule(IrBinary, op="prepend")
    def insert(self, node: IrBinary) -> IrBinary:
        if not isinstance(node.left, IrData):
            return node
        if not isinstance(node.right, IrLiteral):
            return node

        nbt_type = access_type(node.left.nbt_type, ListIndex(None), self.ctx)

        if nbt_type is None:
            return node

        casted_value = cast_value(nbt_type, node.right.value, self.ctx)

        if casted_value is None:
            return node

        return replace(node, right=IrLiteral(value=casted_value))
