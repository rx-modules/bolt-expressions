from contextlib import nullcontext, suppress
from dataclasses import dataclass
from typing import (
    Any,
    Iterable,
    TypedDict,
    Union,
    get_args,
    get_type_hints,
    is_typeddict,
)
from beet import Context
from mecha import Visitor, rule
from bolt.utils import internal

from nbtlib import Compound, Float, Int, Byte, Short, Long, Double, Array, ListIndex, Numeric, NamedKey  # type: ignore


from .typing import (
    NbtType,
    NumericNbtValue,
    NbtValue,
    format_type,
    access_type,
    convert_type,
    get_dict_fields,
    is_alias,
    is_array_type,
    is_compound_alias,
    is_fixed_compound,
    is_list_type,
    is_numeric_type,
    is_optional,
    is_type,
    is_typeddict_guard,
    is_union,
    unwrap_optional_type,
)
from .optimizer import (
    IrBinary,
    IrCast,
    IrData,
    IrLiteral,
    IrOperation,
    IrScore,
    IrSource,
)
from .exceptions import TypeCheckDiagnostic, TypeCheckError, get_exception_chain
from .utils import get_globals


__all__ = [
    "TypeCheckFlags",
    "check_union_type",
    "check_typeddict_type",
    "check_expandable_compound_type",
    "check_list_type",
    "check_numeric_type",
    "check_type",
    "TypeChecker",
]


def infer_dict(value: dict[str, NbtValue]) -> NbtType | None:
    return convert_type({key: infer_type(val) for key, val in value.items()})


def infer_list(value: list[NbtValue]) -> NbtType:
    if not len(value):
        return list[Any]

    options = tuple(infer_type(element) for element in value)

    return list[Union[options]]  # type: ignore


def infer_type(value: NbtValue) -> NbtType | None:
    if isinstance(value, dict):
        return infer_dict(value)

    if isinstance(value, list):
        return infer_list(value)

    return convert_type(type(value))


NUMERIC_ORDER = (Byte, Short, Int, Long, Float, Double)


class TypeCheckFlags(TypedDict, total=False):
    suppress: bool
    numeric_match: bool
    ignore_missing_keys: bool


def check_union_type(
    write: NbtType,
    read: NbtType,
    ctx: Context | None = None,
    **flags: Any,
) -> bool:
    if is_union(read):
        return all(check_type(write, r, ctx, **flags) for r in get_args(read))

    if is_union(write):
        flags = {**flags, "suppress": True}

        if not any(check_type(w, read, ctx, **flags) for w in get_args(write)):
            raise TypeCheckError(
                f'"{format_type(read)}" is not compatible with "{format_type(write)}".'
            )

        return True

    return False


def check_typeddict_type(
    write: type[TypedDict],
    read: NbtType,
    ctx: Context | None = None,
    **flags: Any,
) -> bool:
    if not is_fixed_compound(read):
        raise TypeCheckError(
            f'"{format_type(read)}" is not a compound type with fixed keys and is not compatible with "{format_type(write)}".'
        )

    if write is read:
        return True

    new_flags = {"numeric_match": True, **flags, "ignore_missing_keys": False}

    write_annotations = get_dict_fields(write, ctx)
    read_annotations = get_dict_fields(read, ctx)

    opt_keys = set(write.__optional_keys__)
    opt_keys.update(
        name for name, type in write_annotations.items() if is_optional(type)
    )

    for key, key_type in write_annotations.items():
        if key not in read_annotations:
            if key in opt_keys or flags.get("ignore_missing_keys"):
                continue

            raise TypeCheckError(
                f'"{format_type(read)}" is missing required key "{key}" of type "{format_type(key_type)}".'
            )

        try:
            if not check_type(
                write_annotations[key], read_annotations[key], ctx, **new_flags
            ):
                return False
        except TypeCheckError as cause_exc:
            exc = TypeCheckError(
                f'Key "{key}" of "{format_type(read)}" is incompatible with "{format_type(write)}":'
            )
            raise exc from cause_exc

    for key in read_annotations:
        if key not in write_annotations:
            raise TypeCheckError(
                f'"{format_type(read)}" has extra key "{key}" not present in "{format_type(write)}".'
            )

    return True


def check_expandable_compound_type(
    write: type[dict[str, Any]],
    read: NbtType,
    ctx: Context | None = None,
    **flags: Any,
) -> bool:
    flags = {"numeric_match": True, **flags, "ignore_missing_keys": False}

    child_type = access_type(write, NamedKey(""))

    if is_alias(read, Compound):
        read_child_type = access_type(read, NamedKey(""))

        try:
            return check_type(child_type, read_child_type, ctx, **flags)
        except TypeCheckError as cause_exc:
            exc = TypeCheckError(
                f'"{format_type(read)}" and "{format_type(write)}" have incompatible key types:'
            )
            raise exc from cause_exc

    if is_fixed_compound(read):
        if isinstance(read, dict):
            read_annotations = read
        else:
            read_annotations = get_type_hints(read, get_globals(read, ctx))

        for key, type in read_annotations.items():
            type = unwrap_optional_type(type)

            try:
                if not check_type(child_type, type, ctx, **flags):
                    return False
            except TypeCheckError as cause_exc:
                exc = TypeCheckError(
                    f'"{format_type(read)}" key "{key}" is not valid key of "{format_type(write)}":'
                )
                raise exc from cause_exc

        return True

    raise TypeCheckError(
        f'"{format_type(read)}" is not a compound type and is not compatible with "{format_type(write)}".'
    )


def check_list_type(
    write: type[list[Any] | Array],
    read: NbtType,
    ctx: Context | None = None,
    **flags: Any,
) -> bool:
    flags = {**flags, "numeric_match": True, "ignore_missing_keys": False}

    subtype = access_type(write, ListIndex(None))
    read_subtype = access_type(read, ListIndex(None))

    if read_subtype is None:
        raise TypeCheckError(
            f'"{format_type(read)}" is not a list/array type and is not compatible with "{format_type(write)}".'
        )

    try:
        return check_type(subtype, read_subtype, ctx, **flags)
    except TypeCheckError as cause_exc:
        exc = TypeCheckError(
            f'Elements of "{format_type(read)}" and "{format_type(write)}" are not compatible:'
        )
        raise exc from cause_exc


def check_numeric_type(write: type[NumericNbtValue], read: Any, **flags: Any) -> bool:
    if not issubclass(read, Numeric):
        raise TypeCheckError(
            f'"{format_type(read)}" is not a numeric type and is not compatible with "{format_type(write)}".'
        )

    numeric_match = flags.get("numeric_match", False)

    write_order = NUMERIC_ORDER.index(write)
    read_order = NUMERIC_ORDER.index(read)

    if numeric_match and write_order < read_order:
        raise TypeCheckError(
            f'"{format_type(read)}" cannot be implicitly narrowed to "{format_type(write)}".'
        )

    if numeric_match and read_order < write_order:
        raise TypeCheckError(
            f'"{format_type(read)}" cannot be implicitly converted to "{format_type(write)}".'
        )

    return True


def check_type(
    write: NbtType | None,
    read: NbtType,
    ctx: Context | None = None,
    **flags: Any,
) -> bool:
    """Checks if the type `read` is compatible with the type `write`."""

    context = suppress(TypeCheckError) if flags.get("suppress") else nullcontext()
    flags = {**flags, "suppress": False}

    result = False

    with context:
        if write is None:
            return False

        if write is Any or read is Any:
            return True

        if is_union(write) or is_union(read):
            return check_union_type(write, read, ctx, **flags)

        if is_typeddict_guard(write):
            return check_typeddict_type(write, read, ctx, **flags)

        if is_compound_alias(write):
            return check_expandable_compound_type(write, read, ctx, **flags)

        if is_list_type(write) or is_array_type(write):
            return check_list_type(write, read, ctx, **flags)

        if is_numeric_type(write):
            return check_numeric_type(write, read, **flags)

        if convert_type(write) != convert_type(read):
            raise TypeCheckError(
                f'"{format_type(read)}" does not match "{format_type(write)}".'
            )

        result = True

    return result


@dataclass(eq=False, kw_only=True)
class TypeChecker(Visitor):
    ctx: Context | None

    @internal
    def __call__(self, nodes: Iterable[IrOperation]) -> Iterable[IrOperation]:  # type: ignore
        for node in nodes:
            exc = self.invoke(node)

            if exc is not None:
                raise exc

            yield node

    def get_type(self, node: IrSource | IrLiteral) -> NbtType:
        if isinstance(node, IrData):
            return node.nbt_type
        elif isinstance(node, IrScore):
            return Int
        elif isinstance(node, IrLiteral):
            t = infer_type(node.value)
            return t if t is not None else Any

        return Any

    def check_type(
        self,
        former: IrSource,
        latter: IrSource | IrLiteral,
        write: NbtType | None = None,
        read: NbtType | None = None,
        **flags: Any,
    ) -> tuple[bool, tuple[BaseException, ...]]:
        if write is None:
            write = self.get_type(former)
        if read is None:
            read = self.get_type(latter)

        match = False
        errors: tuple[BaseException, ...] = ()
        # require numeric types to match if right side is literal, that means
        # it fails only if a literal failed to be casted to the right type.
        flags = {"numeric_match": isinstance(latter, IrLiteral), **flags}

        try:
            match = check_type(write, read, self.ctx, **flags)
        except TypeCheckError as exc:
            errors = get_exception_chain(exc)

        return match, errors

    def format_operand(self, value: IrSource | IrLiteral, read: NbtType | None = None):
        if read is None:
            read = self.get_type(value)

        if isinstance(value, IrData):
            return f'{value.type} "{value.target} {value.path}" of type "{format_type(read)}"'
        if isinstance(value, IrScore):
            return f'score "{value.holder} {value.obj}"'
        return f'value of type "{format_type(read)}"'

    def format_errors(self, errors: Any) -> str:
        return "".join("\n  - " + str(e) for e in errors)

    def create_diagnostic(
        self,
        pattern: str,
        *args: NbtType
        | tuple[IrSource | IrLiteral, NbtType]
        | tuple[Any, ...]
        | IrSource
        | IrLiteral
        | Any,
    ) -> TypeCheckDiagnostic:
        values: list[str] = []

        for arg in args:
            if is_type(arg):
                value = format_type(arg)
            elif isinstance(arg, tuple):
                if len(arg) == 2 and isinstance(arg[0], (IrSource, IrLiteral)):
                    value = self.format_operand(arg[0], arg[1])
                elif len(arg) and isinstance(arg[0], TypeCheckError):
                    value = self.format_errors(arg)
                else:
                    value = "".join(str(el) for el in arg)
            elif isinstance(arg, (IrSource, IrLiteral)):
                value = self.format_operand(arg)
            else:
                value = str(arg)

            values.append(value)

        fmt = pattern % tuple(values)
        msg = fmt[0].capitalize() + fmt[1:]
        return TypeCheckDiagnostic(msg)

    @rule(IrOperation)
    def fallback(self, node: IrOperation) -> None:
        ...

    @rule(IrCast)
    def set(self, node: IrCast) -> TypeCheckDiagnostic | None:
        write = node.cast_type
        matched, errors = self.check_type(node.left, node.right, write)

        if not matched:
            return self.create_diagnostic(
                "%s cannot be assigned to %s: %s",
                node.right,
                (node.left, write),
                errors,
            )

    @rule(IrBinary, op="append")
    @rule(IrBinary, op="prepend")
    @rule(IrBinary, op="insert")
    def insert(self, node: IrBinary) -> TypeCheckDiagnostic | None:
        write = access_type(self.get_type(node.left), ListIndex(None))

        if write is None:
            return self.create_diagnostic(
                '%s is not a list/array and does not support "%s".', node.left, node.op
            )

        matched, errors = self.check_type(
            node.left, node.right, write, numeric_match=True
        )

        if not matched:
            if node.op == "append":
                msg = "appended to"
            elif node.op == "prepend":
                msg = "prepended to"
            else:
                msg = "inserted into"

            return self.create_diagnostic(
                "%s cannot be %s %s: %s",
                node.right,
                msg,
                node.left,
                errors,
            )

    @rule(IrBinary, op="merge")
    def merge(self, node: IrBinary) -> TypeCheckDiagnostic | None:
        matched, errors = self.check_type(
            node.left, node.right, ignore_missing_keys=True
        )

        if not matched:
            return self.create_diagnostic(
                "%s cannot be merged with %s: %s",
                node.right,
                node.left,
                errors,
            )
