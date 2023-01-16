import sys
from types import GenericAlias, NoneType, UnionType

from nbtlib import (  # type: ignore
    Array,
    Base,
    Byte,
    Compound,
    CompoundMatch,
    Double,
    End,
    Float,
    Int,
    List,
    ListIndex,
    Long,
    NamedKey,
    Numeric,
    Path,
    Short,
    String,
)

from .literals import convert_tag

from typing import Any, Iterable, TypedDict, Union, _UnionGenericAlias, get_args, get_origin, get_type_hints, is_typeddict  # type: ignore isort: skip


__all__ = [
    "is_type",
    "convert_type",
    "get_property_type",
    "get_subtype_from_accessor",
    "check_type",
    "check_union_type",
    "check_typeddict_type",
    "check_expandable_compound_type",
]


DataType = Union[type, GenericAlias, UnionType, TypedDict, dict[str, "DataType"], None]

Accessor = Union[NamedKey, ListIndex, CompoundMatch]


def is_union(value: Any) -> bool:
    return isinstance(value, (UnionType, _UnionGenericAlias))


def is_optional(value: Any) -> bool:
    if not is_union(value):
        return False

    return NoneType in get_args(value)


def is_alias(value: Any, origin: type | Iterable[type] = None) -> bool:
    if not isinstance(value, GenericAlias):
        return False

    if origin is not None:
        return issubclass(get_origin(value), origin)

    return True


def get_optional_type(value: UnionType):
    if not is_union(value):
        return value

    return Union[tuple(v for v in get_args(value) if v is not NoneType)]  # type: ignore


def is_type(value: DataType | Any) -> bool:
    if isinstance(value, dict):
        return any(is_type(v) for v in value.values())

    return value in (Any, None) or isinstance(
        value, (type, UnionType, _UnionGenericAlias, GenericAlias)
    )


def convert_type(value: DataType) -> DataType:
    if isinstance(value, dict):
        value = {key: convert_type(v) for key, v in value.items()}
        return TypedDict("TypedDict", value)  # type: ignore

    if is_typeddict(value):
        return value

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
        if issubclass(value, bool):
            return Byte
        if issubclass(value, int):
            return Int
        if issubclass(value, float):
            return Float
        if issubclass(value, dict):
            return Compound
        if issubclass(value, list):
            return List

    return value


################
# TYPE CHECKING
################

NUMERIC_ORDER = (Byte, Short, Int, Long, Float, Double)


def check_union_type(write: DataType, read: DataType) -> bool:
    if is_union(read):
        return all(check_type(write, r) for r in get_args(read))

    if is_union(write):
        return any(check_type(w, read) for w in get_args(write))

    return False


def check_typeddict_type(write: TypedDict, read: DataType) -> bool:
    if not is_typeddict(read):
        # read value is not a compound with fixed keys
        return False

    if write is read:
        return True

    write_annotations = write.__annotations__
    read_annotations = read.__annotations__

    opt_keys = set(write.__optional_keys__)
    opt_keys.update(
        name for name, type in write_annotations.items() if is_optional(type)
    )

    for key in write_annotations:
        if key not in read_annotations:
            if key in opt_keys:
                continue

            # missing required key
            return False

        if not check_type(write_annotations[key], read_annotations[key]):
            # type of key is not compatible with write key type
            return False

    for key in read_annotations:
        if key not in write_annotations:
            # type has extra key
            return False

    return True


def check_expandable_compound_type(write: GenericAlias, read: DataType) -> bool:
    child_type = get_args(write)[0]

    if is_alias(read, Compound):
        read_child_type = get_args(read)[0]

        return check_type(child_type, read_child_type)

    if is_typeddict(read):
        for type in read.__annotations__.values():
            if is_optional(type):
                type = get_optional_type(type)

            if not check_type(child_type, type):
                return False

        return True

    return False


def check_list_type(write: List | Array, read: DataType) -> bool:
    subtype = write.subtype if issubclass(write, List) else write.wrapper

    if issubclass(read, List):
        read_subtype = read.subtype
    elif issubclass(read, Array):
        read_subtype = read.wrapper
    else:
        # read is not list/array
        return False

    return check_type(subtype, read_subtype)


def check_numeric_type(write: Numeric, read: Any) -> bool:
    if not issubclass(read, Numeric):
        # read is not a number
        return False

    if NUMERIC_ORDER.index(write) < NUMERIC_ORDER.index(read):
        # read type cannot be represented by write type (loss of magnitude)
        return False

    return True


def check_type(write: DataType, read: DataType) -> bool:
    """Checks if the type `read` is compatible with the type `write`."""

    if write is None:
        return False

    if write is Any or read is Any:
        return True

    if is_union(write) or is_union(read):
        return check_union_type(write, read)

    if is_typeddict(write):
        return check_typeddict_type(write, read)

    if is_alias(write, Compound):
        return check_expandable_compound_type(write, read)

    if issubclass(write, (List, Array)):
        return check_list_type(write, read)

    if issubclass(write, Numeric):
        return check_numeric_type(write, read)

    return convert_type(write) == convert_type(read)


#################
# TYPE ACCESS
#################


def get_property_type(type: DataType, path: Path | tuple[Accessor, ...]) -> DataType:
    new_accessors: tuple[Accessor, ...] = tuple(path)

    for accessor in new_accessors:
        type = get_subtype_from_accessor(accessor, type)

    return type


def get_subtype_from_accessor(accessor: Accessor, current_type: DataType) -> DataType:
    if current_type is NoneType:
        return None

    if isinstance(current_type, _UnionGenericAlias):
        args = get_args(current_type)
        subtypes = tuple(get_subtype_from_accessor(accessor, arg) for arg in args)

        return Union[subtypes]  # type: ignore

    if isinstance(accessor, NamedKey):
        key = accessor.key

        match current_type:
            case GenericAlias() as alias if issubclass(alias.__origin__, Compound):
                args = get_args(alias)

                if not args:
                    return Any

                return args[-1]
            case value if is_typeddict(value):
                fields = get_type_hints(value)

                if key not in fields:
                    # TODO: emit warning: Key '{key}' is not present on compound of type {current_type}
                    ...

                return convert_type(fields.get(key, Any))
            case value if value is Any:
                return Any
            case _:
                # TODO: emit warning: Cannot access named keys from type {current_type}
                return Any

    if isinstance(accessor, ListIndex):
        # index = accessor.index

        match current_type:
            case type() as list if issubclass(list, List):
                return list.subtype if not issubclass(list.subtype, End) else Any  # type: ignore
            case type() as array if issubclass(array, Array):
                return array.wrapper if array.wrapper is not None else Any
            case value if value is Any:
                return Any
            case _:
                # TODO: emit warning: Cannot access elements by index from type {current_type}
                return Any

    # CompoundMatch
    match current_type:
        case GenericAlias() as alias if issubclass(alias.__origin__, Compound):
            return current_type
        case value if is_typeddict(value):
            return current_type
        case value if value is Any:
            return Any
        case _:
            # TODO: emit warning: Cannot match compound from type {current_type}
            return Any
