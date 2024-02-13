from types import GenericAlias, NoneType, UnionType
from frozendict import frozendict
from typing import (
    Any,
    Iterable,
    Literal,
    TypeGuard,
    TypedDict,
    Union,
    _UnionGenericAlias,  # type: ignore
    cast,
    get_args,
    get_origin,
    get_type_hints,
    is_typeddict,
)
from beet import Context

from nbtlib import End, Compound, Float, Int, List, String, Byte, Short, Long, Double, Array, NamedKey, ListIndex, CompoundMatch  # type: ignore

from .utils import format_name, get_globals, type_name  # type: ignore


__all__ = ["is_type", "convert_type", "literal_types"]


NBT_TYPE_STRING = ("byte", "short", "int", "long", "float", "double")
NbtTypeString = Literal["byte", "short", "int", "long", "float", "double"]


NumericNbtValue = Byte | Short | Int | Long | Float | Double
NbtValue = NumericNbtValue | String | List | Array | Compound

NbtType = Union[
    # numeric
    type[NumericNbtValue],
    # string
    type[str],
    # array
    type[Array],
    # lists
    type[list["NbtType"]],
    # compounds
    # type[TypedDict],
    type[dict[str, "NbtType"]],
    dict[str, "NbtType"],
    # unions
    UnionType,
    # any
    type[Any],
]


literal_types: dict[str, type[NbtValue]] = {
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


def format_type(t: Any, *, __refs: list[Any] | None = None) -> str:
    if __refs is None:
        __refs = []

    circular_ref = t in __refs
    __refs.append(t)

    if t in (None, NoneType):
        return "None"

    if isinstance(t, (UnionType, _UnionGenericAlias)):
        return " | ".join(format_type(x, __refs=__refs) for x in get_args(t))

    if isinstance(t, GenericAlias):
        origin = format_type(get_origin(t), __refs=__refs)
        args = (format_type(x, __refs=__refs) for x in get_args(t))

        if circular_ref:
            return f"{origin}[...]"

        return f"{origin}[{', '.join(args)}]"

    if is_typeddict_guard(t) and t.__name__ == "__anonymous_dict__":
        t = get_dict_fields(t)
    if isinstance(t, dict):
        t_dict = cast(dict[str, Any], t)

        if circular_ref:
            return "{...}"

        return (
            "{"
            + ", ".join(
                f"{key}: {format_type(val, __refs=__refs)}"
                for key, val in t_dict.items()
            )
            + "}"
        )

    return format_name(t)


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
        case float():
            return Float(value)
        case int():
            return Int(value)
        case str():
            return String(value)
        case _:
            return None


def is_typeddict_guard(value: Any) -> TypeGuard[type[TypedDict]]:
    return is_typeddict(value)


def is_alias(value: Any, origin: type | tuple[type, ...] | None = None) -> bool:
    if not isinstance(value, GenericAlias):
        return False

    if origin is not None:
        value_origin = get_origin(value)

        if not isinstance(value_origin, type):
            return False

        return issubclass(value_origin, origin)

    return True


def is_union(value: Any) -> bool:
    return isinstance(value, (UnionType, _UnionGenericAlias))


def is_optional(value: Any) -> bool:
    if not is_union(value):
        return False

    return NoneType in get_args(value)


def is_numeric_type(value: Any) -> TypeGuard[type[NumericNbtValue]]:
    return isinstance(value, type) and issubclass(value, (int, float))


def is_string_type(value: Any) -> TypeGuard[type[String]]:
    return isinstance(value, type) and issubclass(value, str)


def is_list_type(value: Any) -> TypeGuard[type[list[Any]]]:
    if is_alias(value):
        return is_alias(value, list)

    if not isinstance(value, type):
        return False

    return issubclass(value, list)


def is_array_type(value: Any) -> TypeGuard[type[Array]]:
    return isinstance(value, type) and issubclass(value, Array)


def is_compound_alias(value: Any) -> TypeGuard[type[dict[str, Any]]]:
    if is_alias(value):
        return is_alias(value, dict)

    return isinstance(value, type) and issubclass(value, dict)


def is_fixed_compound(value: Any) -> TypeGuard[dict[str, Any] | type[TypedDict]]:
    return isinstance(value, dict) or is_typeddict(value)


def is_compound_type(value: Any) -> TypeGuard[type[dict[str, Any]] | type[TypedDict]]:
    return is_compound_alias(value) or is_fixed_compound(value)


def unwrap_optional_type(value: Any) -> Any:
    if not is_union(value):
        return value

    args = get_args(value)

    if NoneType not in args:
        return value

    return Union[tuple(v for v in args if v is not NoneType)]  # type: ignore


def get_dict_fields(
    t: type[TypedDict] | dict[str, Any], ctx: Context | None = None
) -> dict[str, NbtType]:
    globalns = None

    if isinstance(t, dict):
        fields = t
    else:
        globalns = get_globals(t, ctx)
        fields = get_type_hints(t, globalns=globalns)

    result: dict[str, NbtType] = {}

    for key, value in fields.items():
        value_type = convert_type(value, globalns=globalns)
        result[key] = value_type if value_type is not None else Any

    return dict(result)


def is_type(value: Any, allow_dict: bool = True) -> TypeGuard[NbtType]:
    if allow_dict and isinstance(value, dict):
        value = cast(dict[Any, Any], value)
        return any(is_type(v) for v in value.values())

    return value in (Any, None) or isinstance(
        value, (type, UnionType, _UnionGenericAlias, GenericAlias)
    )


def convert_type(
    value: Any, is_origin: bool = False, globalns: dict[str, Any] | None = None
) -> NbtType | None:
    if value is Any:
        return Any

    if value in (None, NoneType):
        return None

    if isinstance(value, dict):
        value = cast(dict[str, Any], value)

        type_dict: dict[str, NbtType] = {}
        for key, val in value.items():
            val_type = convert_type(val, globalns=globalns)
            type_dict[key] = val_type if val_type is not None else Any

        return TypedDict("__anonymous_dict__", type_dict)  # type: ignore

    if is_typeddict(value):
        return value  # type: ignore

    if is_alias(value, Compound):
        args = get_args(value)
        return convert_type(dict[str, args[0]], globalns=globalns)  # type: ignore

    if isinstance(value, (UnionType, _UnionGenericAlias)):
        args = get_args(value)
        converted = tuple(convert_type(arg, globalns=globalns) for arg in args)

        return Union[converted]  # type: ignore

    if isinstance(value, GenericAlias):
        args = get_args(value)

        converted = tuple(convert_type(arg, globalns=globalns) for arg in args)
        origin = convert_type(value.__origin__, is_origin=True)

        if isinstance(origin, type) and issubclass(origin, Compound):
            converted = (converted[-1],)

        if len(converted) == 1:
            converted = converted[0]

        return origin[converted]  # type: ignore

    if isinstance(value, type):
        if issubclass(value, (Byte, Short, Long, Double, Array)):
            return value
        if issubclass(value, bool):
            return Byte
        if issubclass(value, (float, Float)):
            return Float
        if issubclass(value, (int, Int)):
            return Int
        if issubclass(value, str):
            return String
        if issubclass(value, dict):
            return dict if is_origin else convert_type(dict[str, Any])  # type: ignore
        if issubclass(value, List):
            subtype = Any if value.subtype is End else value.subtype
            return list[convert_type(subtype)]  # type: ignore
        if issubclass(value, list):
            return list if is_origin else list[Any]  # type: ignore

    if isinstance(value, str) and globalns is not None and value in globalns:
        return globalns[value]

    raise TypeError(f"type {type_name(value)} cannot be converted to nbt type.")


Accessor = Union[NamedKey, ListIndex, CompoundMatch]


def access_type_by_path(
    t: NbtType | None, path: Iterable[Accessor], ctx: Context | None = None
) -> NbtType | None:
    new_accessors: tuple[Accessor, ...] = tuple(path)

    for accessor in new_accessors:
        t = access_type(t, accessor, ctx)

    return t


class A(TypedDict):
    a: str
    b: int


def access_typeddict(
    t: type[TypedDict], accessor: Accessor, ctx: Context | None = None
) -> NbtType | None:
    if isinstance(accessor, CompoundMatch):
        return t

    if isinstance(accessor, NamedKey):
        key = accessor.key

        fields = get_dict_fields(t, ctx)

        if attr_type := fields.get(key):
            result = convert_type(attr_type)
            return result if result is not None else Any

    return None


def access_compound_alias(
    t: type[dict[str, Any]], accessor: Accessor
) -> NbtType | None:
    if isinstance(accessor, CompoundMatch):
        return t

    if isinstance(accessor, NamedKey):
        args = get_args(t)

        if not args:
            return Any

        return args[-1]

    return None


def access_list(t: type[list[Any]], accessor: Accessor) -> NbtType | None:
    if isinstance(accessor, ListIndex):
        if is_alias(t, list):
            arg = get_args(t)
            return arg[0] if arg else Any

        if isinstance(t, type) and issubclass(t, List):
            if t.subtype is End:
                return Any
            return t.subtype

    return None


def access_array(t: type[Array], accessor: Accessor) -> NbtType | None:
    if isinstance(accessor, ListIndex):
        wrapper = t.wrapper
        return wrapper if wrapper is not None else Any

    return None


def access_type(
    current_type: NbtType | None, accessor: Accessor, ctx: Context | None = None
) -> NbtType | None:
    if current_type in (Any, None):
        return current_type

    if is_numeric_type(current_type) or is_string_type(current_type):
        return None

    if is_union(current_type):
        args = get_args(current_type)
        subtypes = tuple(access_type(arg, accessor) for arg in args)

        return convert_type(Union[subtypes])  # type: ignore

    if is_typeddict_guard(current_type):
        return access_typeddict(current_type, accessor, ctx)

    if is_compound_alias(current_type):
        return access_compound_alias(current_type, accessor)

    if is_list_type(current_type):
        return access_list(current_type, accessor)

    if is_array_type(current_type):
        return access_array(current_type, accessor)

    return None
