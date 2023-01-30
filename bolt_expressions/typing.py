from contextlib import nullcontext, suppress
from dataclasses import dataclass, field, replace
from types import GenericAlias, NoneType, UnionType
from typing import _UnionGenericAlias  # type: ignore
from typing import (
    Any,
    Iterable,
    Literal,
    Type,
    TypedDict,
    Union,
    cast,
    get_args,
    get_origin,
    get_type_hints,
    is_typeddict,
    overload,
)

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
    Short,
    String,
)

from .exceptions import TypeCheckError
from .literals import convert_tag

__all__ = [
    "DataType",
    "Accessor",
    "type_name",
    "format_type",
    "is_union",
    "is_optional",
    "is_alias",
    "is_numeric",
    "get_optional_type",
    "is_type",
    "convert_type",
    "NumericValue",
    "NbtValue",
    "infer_dict",
    "infer_list",
    "infer_type",
    "cast_dict",
    "cast_list",
    "cast_numeric",
    "cast_string",
    "cast_value",
    "check_union_type",
    "check_typeddict_type",
    "check_expandable_compound_type",
    "check_list_type",
    "check_numeric_type",
    "check_type",
    "get_property_type_by_path",
    "get_subtype_by_accessor",
    "DataNode",
]


DataType = Union[type, GenericAlias, UnionType, TypedDict, dict[str, "DataType"], None]

Accessor = Union[NamedKey, ListIndex, CompoundMatch]


def is_union(value: Any) -> bool:
    return isinstance(value, (UnionType, _UnionGenericAlias))


def is_optional(value: Any) -> bool:
    if not is_union(value):
        return False

    return NoneType in get_args(value)


def is_alias(value: Any, origin: type | tuple[type] | None = None) -> bool:
    if not isinstance(value, GenericAlias):
        return False

    if origin is not None:
        value_origin = get_origin(value)

        if not isinstance(value_origin, type):
            return False

        return issubclass(value_origin, origin)

    return True


def is_numeric(value: Any) -> bool:
    return isinstance(value, type) and issubclass(value, Numeric)


def get_optional_type(value: UnionType) -> DataType:
    if not is_union(value):
        return value

    return Union[tuple(v for v in get_args(value) if v is not NoneType)]  # type: ignore


def is_type(value: DataType | Any) -> bool:
    if isinstance(value, dict):
        return any(is_type(v) for v in value.values())

    return value in (Any, None) or isinstance(
        value, (type, UnionType, _UnionGenericAlias, GenericAlias)
    )


def type_name(t: DataType) -> str:
    if not isinstance(t, type):
        return repr(t)

    if issubclass(t, (bool, int, float, str, list, dict, Base)):
        return t.__name__

    return f"{t.__module__}.{t.__name__}"


def format_type(t: DataType, *, __refs: Any = None) -> str:
    if __refs is None:
        __refs = []

    circular_ref = t in __refs
    __refs.append(t)

    if is_union(t):
        return " | ".join(format_type(x, __refs=__refs) for x in get_args(t))

    if is_alias(t):
        origin = format_type(get_origin(t), __refs=__refs)
        args = (format_type(x, __refs=__refs) for x in get_args(t))

        if circular_ref:
            return f"{origin}[...]"

        return f"{origin}[{', '.join(args)}]"

    if is_typeddict(t) and type_name(t) == "TypedDict":
        if circular_ref:
            return "{...}"

        return (
            "{"
            + ", ".join(
                f"{key}: {format_type(val, __refs=__refs)}"
                for key, val in t.__annotations__.items()
            )
            + "}"
        )

    return type_name(t)


@overload
def convert_type(
    value: dict[str, DataType], typeddict: Literal[True] = True
) -> Type[TypedDict]:
    ...


@overload
def convert_type(
    value: dict[str, DataType], typeddict: Literal[False]
) -> dict[str, DataType]:
    ...


@overload
def convert_type(value: type, typeddict: bool = True) -> type:
    ...


@overload
def convert_type(value: DataType, typeddict: bool = True) -> DataType:
    ...


def convert_type(value: DataType, typeddict: bool = True) -> DataType:
    if isinstance(value, dict):
        value = {key: convert_type(v, typeddict=typeddict) for key, v in value.items()}

        if not typeddict:
            return value

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

        if issubclass(origin, Compound):
            converted = (converted[-1],)

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
# TYPE INFERENCE
################

NumericValue = Byte | Short | Int | Long | Float | Double

NbtValue = dict[str, "NbtValue"] | list["NbtValue"] | String | NumericValue


def infer_dict(value: dict[str, NbtValue]) -> DataType:
    return convert_type({key: infer_type(val) for key, val in value.items()})


def infer_list(value: list[NbtValue]) -> DataType:
    if not len(value):
        return List

    options = tuple(infer_type(element) for element in value)

    return List[Union[options]]  # type: ignore


def infer_type(value: NbtValue) -> DataType:
    if isinstance(value, dict):
        return infer_dict(value)

    if isinstance(value, list):
        return infer_list(value)

    return convert_type(type(value))


################
# TYPE CASTING
################


def cast_dict(type: DataType, value: dict[Any, Any]) -> Compound | None:
    result: dict[Any, Any] = {}

    for key, val in value.items():
        cast_val = val

        subtype = get_subtype_by_accessor(NamedKey(key), type)

        if subtype and (v := cast_value(subtype, val)):
            cast_val = v

        result[key] = cast_val

    return Compound(result)


def cast_list(datatype: DataType, value: list[Any] | Array) -> List | Array | None:
    if not (isinstance(datatype, type) and issubclass(datatype, (List, Array))):
        return None

    result: list[Any] = []

    for i, element in enumerate(value):
        subtype = get_subtype_by_accessor(ListIndex(i), datatype)

        if subtype is None:
            return None

        element = cast_value(subtype, element)

        if element is None:
            return None

        result.append(element)

    datatype = datatype if issubclass(datatype, Array) else List

    try:
        return datatype(result)
    except:
        return None


def cast_numeric(datatype: DataType, value: int | float) -> Numeric | None:
    if not is_numeric(datatype):
        return None

    datatype = cast(Type[NumericValue], datatype)

    try:
        return datatype(value)
    except:
        return None


def cast_string(datatype: DataType, value: str) -> String | None:
    if isinstance(datatype, type) and issubclass(datatype, str):
        return String(value)

    return None


def cast_value(datatype: DataType, value: NbtValue | Any) -> Any | None:
    if datatype in (Any, None, NoneType) or is_union(datatype):
        return convert_tag(value)

    if isinstance(value, dict):
        return cast_dict(datatype, value)

    if isinstance(value, list):
        return cast_list(datatype, value)

    if isinstance(value, (int, float)):
        return cast_numeric(datatype, value)

    if isinstance(value, str):
        return cast_string(datatype, value)

    return convert_tag(value)


################
# TYPE CHECKING
################

NUMERIC_ORDER = (Byte, Short, Int, Long, Float, Double)


def check_union_type(write: DataType, read: DataType, **flags: bool) -> bool:
    if is_union(read):
        return all(check_type(write, r, **flags) for r in get_args(read))

    if is_union(write):
        flags = {**flags, "suppress": True}

        if not any(check_type(w, read, **flags) for w in get_args(write)):
            raise TypeCheckError(
                f"'{format_type(read)}' is not compatible with '{format_type(write)}'."
            )

        return True

    return False


def check_typeddict_type(write: Type[TypedDict], read: DataType, **flags: bool) -> bool:
    if not is_typeddict(read):
        raise TypeCheckError(
            f"'{format_type(read)}' is not a compound type with fixed keys and is not compatible with '{format_type(write)}'."
        )

    if write is read:
        return True

    flags = {"numeric_widening": False, "numeric_narrowing": False, **flags}

    write_annotations = write.__annotations__
    read_annotations = read.__annotations__

    opt_keys = set(write.__optional_keys__)
    opt_keys.update(
        name for name, type in write_annotations.items() if is_optional(type)
    )

    for key, key_type in write_annotations.items():
        if key not in read_annotations:
            if key in opt_keys:
                continue

            raise TypeCheckError(
                f"'{format_type(read)}' is missing required key '{key}' of type '{format_type(key_type)}'."
            )

        try:
            if not check_type(write_annotations[key], read_annotations[key], **flags):
                return False
        except TypeCheckError as cause_exc:
            exc = TypeCheckError(
                f"'{format_type(read)}' key '{key}' is incompatible with key of '{format_type(write)}':"
            )
            raise exc from cause_exc

    for key in read_annotations:
        if key not in write_annotations:
            raise TypeCheckError(
                f"'{format_type(read)}' has extra key '{key}' not present in '{format_type(write)}'."
            )

    return True


def check_expandable_compound_type(
    write: GenericAlias, read: DataType, **flags: bool
) -> bool:
    flags = {"numeric_widening": False, "numeric_narrowing": False, **flags}

    child_type = get_args(write)[0]

    if is_alias(read, Compound):
        read_child_type = get_args(read)[0]

        try:
            return check_type(child_type, read_child_type, **flags)
        except TypeCheckError as cause_exc:
            exc = TypeCheckError(
                f"'{format_type(read)}' and '{format_type(write)}' have incompatible key types:"
            )
            raise exc from cause_exc

    if is_typeddict(read):
        for key, type in read.__annotations__.items():
            if is_optional(type):
                type = get_optional_type(type)

            try:
                if not check_type(child_type, type, **flags):
                    return False
            except TypeCheckError as cause_exc:
                exc = TypeCheckError(
                    f"'{format_type(read)}' key '{key}' is not valid key of '{format_type(write)}':"
                )
                raise exc from cause_exc

        return True

    raise TypeCheckError(
        f"'{format_type(read)}' is not a compound type and is not compatible with '{format_type(write)}'."
    )


def check_list_type(write: Type[List | Array], read: DataType, **flags: bool) -> bool:
    flags = {"numeric_widening": False, "numeric_narrowing": False, **flags}

    subtype = get_subtype_by_accessor(ListIndex(None), write)

    read_subtype = get_subtype_by_accessor(ListIndex(None), read)

    if read_subtype is None:
        raise TypeCheckError(
            f"'{format_type(read)}' is not list/array type and is not compatible with '{format_type(write)}'."
        )

    try:
        return check_type(subtype, read_subtype, **flags)
    except TypeCheckError as cause_exc:
        exc = TypeCheckError(
            f"'{format_type(read)}' and '{format_type(write)}' element types are not compatible:"
        )
        raise exc from cause_exc


def check_numeric_type(write: Type[Numeric], read: Any, **flags: bool) -> bool:
    if not issubclass(read, Numeric):
        raise TypeCheckError(
            f"'{format_type(read)}' is not a numeric type and is not compatible with '{format_type(write)}'."
        )

    write_order = NUMERIC_ORDER.index(write)
    read_order = NUMERIC_ORDER.index(read)

    if not flags.get("numeric_narrowing", True) and write_order < read_order:
        raise TypeCheckError(
            f"'{format_type(read)}' cannot be implicitly narrowed to '{format_type(write)}'."
        )

    if not flags.get("numeric_widening", True) and read_order < write_order:
        raise TypeCheckError(
            f"'{format_type(read)}' cannot be implicitly converted to '{format_type(write)}'."
        )

    return True


def check_type(write: DataType, read: DataType, **flags: bool) -> bool:
    """Checks if the type `read` is compatible with the type `write`."""

    ctx = suppress(TypeCheckError) if flags.get("suppress") else nullcontext()
    flags = {**flags, "suppress": False}

    result = False

    with ctx:
        if write is None:
            return False

        if write is Any or read is Any:
            return True

        if is_union(write) or is_union(read):
            return check_union_type(write, read, **flags)

        if is_typeddict(write):
            write = cast(Type[TypedDict], write)
            return check_typeddict_type(write, read, **flags)

        if is_alias(write, Compound):
            write = cast(GenericAlias, write)
            return check_expandable_compound_type(write, read, **flags)

        if isinstance(write, type):
            if issubclass(write, (List, Array)):
                return check_list_type(write, read, **flags)

            if issubclass(write, Numeric):
                return check_numeric_type(write, read, **flags)

        if convert_type(write) != convert_type(read):
            raise TypeCheckError(
                f"'{format_type(read)}' does not match '{format_type(write)}'."
            )

        result = True

    return result


#################
# TYPE ACCESS
#################


def get_property_type_by_path(type: DataType, path: Iterable[Accessor]) -> DataType:
    new_accessors: tuple[Accessor, ...] = tuple(path)

    for accessor in new_accessors:
        type = get_subtype_by_accessor(accessor, type)

    return type


def get_subtype_by_accessor(accessor: Accessor, current_type: DataType) -> DataType:
    if current_type in (None, NoneType):
        return None

    if isinstance(current_type, _UnionGenericAlias):
        args = get_args(current_type)
        subtypes = tuple(get_subtype_by_accessor(accessor, arg) for arg in args)

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

                return convert_type(fields.get(key))
            case value if value is Any:
                return Any
            case _:
                # TODO: emit warning: Cannot access named keys from type {current_type}
                return None

    if isinstance(accessor, ListIndex):
        # index = accessor.index

        match current_type:
            case type() as list if issubclass(list, List):
                if isinstance(list.subtype, type) and issubclass(list.subtype, End):  # type: ignore
                    return Any
                else:
                    return list.subtype
            case type() as array if issubclass(array, Array):
                return array.wrapper if array.wrapper is not None else Any
            case value if value is Any:
                return Any
            case _:
                # TODO: emit warning: Cannot access elements by index from type {current_type}
                return None

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
            return None


@dataclass
class DataNode:
    type: DataType = None
    children: dict[Accessor, "DataNode"] = field(default_factory=dict)

    def get(self, path: Iterable[Accessor]) -> Union["DataNode", None]:
        node: DataNode | None = self

        for accessor in path:
            node = node.children.get(accessor)

            if not node:
                return None

        return node

    def get_or_create(self, path: Iterable[Accessor] = ()) -> "DataNode":
        node: DataNode = self

        for accessor in path:
            if not accessor in node.children:
                child_type = get_subtype_by_accessor(accessor, node.type)
                node.children[accessor] = DataNode(type=child_type)

            node = node.children[accessor]

        return node

    def get_type(self, path: Iterable[Accessor] = ()) -> DataType:
        path = tuple(path)

        if not path:
            return convert_type(self.type)

        child = self.children.get(path[0])

        if child is None:
            return get_property_type_by_path(self.type, path)

        return child.get_type(path[1:])

    def pop(self, path: Iterable[Accessor]):
        *parent_path, child_accessor = path

        parent = self.get(parent_path)

        if not parent:
            return

        return parent.children.pop(child_accessor, None)

    def copy(self):
        return replace(
            self,
            children={key: child.copy() for key, child in self.children.items()},
        )

    def set_type(self, type: DataType):
        self.type = type
        self.children = {}

    def set_children(self, children: dict[Accessor, "DataNode"]):
        self.children = {key: child.copy() for key, child in children.items()}

    def set_from(self, node: "DataNode"):
        self.set_type(node.type)
        self.set_children(node.children)
