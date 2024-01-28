from contextlib import contextmanager
import sys
from types import GenericAlias, NoneType, UnionType
from typing import Any, Dict, _UnionGenericAlias, cast, get_args, get_origin, is_typeddict # type: ignore
from bolt import Runtime
from nbtlib import Base # type: ignore
from beet import Context

__all__ = [
    "type_name",
    "format_type",
    "identifier_generator",
    "get_globals",
    "assert_exception",
]


def type_name(obj: Any) -> str:
    return type(obj).__name__

def format_name(t: Any) -> str:
    if not isinstance(t, type):
        return repr(t)
        
    if is_typeddict(t):
        return f"{t.__module__}.{t.__name__}"

    if issubclass(t, (bool, int, float, str, list, dict, NoneType, Base)):
        return t.__name__

    return f"{t.__module__}.{t.__name__}"

def format_type(t: Any, *, __refs: list[Any] | None = None) -> str:
    if __refs is None:
        __refs = []

    circular_ref = t in __refs
    __refs.append(t)

    if isinstance(t, (UnionType, _UnionGenericAlias)):
        return " | ".join(format_type(x, __refs=__refs) for x in get_args(t))

    if isinstance(t, GenericAlias):
        origin = format_type(get_origin(t), __refs=__refs)
        args = (format_type(x, __refs=__refs) for x in get_args(t))

        if circular_ref:
            return f"{origin}[...]"

        return f"{origin}[{', '.join(args)}]"

    if isinstance(t, dict):
        t_dict = cast(dict[str, Any], t)
        
        if circular_ref:
            return "{...}"

        return (
            "{"
            + ", ".join(
                f"{key}: {format_type(val, __refs=__refs)}" for key, val in t_dict.items()
            )
            + "}"
        )

    return format_name(t)

def identifier_generator(ctx: Context | None = None):
    if ctx:
        runtime = ctx.inject(Runtime)
        incr: Dict[str, int] = {}

        while True:
            path = runtime.modules.current_path
            incr[path] = incr.setdefault(path, -1) + 1

            yield ctx.generate.format(f"{{hash}}_{incr[path]}", path)
    else:
        counter = 0
        while True:
            yield str(f"i{counter}")


def get_globals(obj: Any, ctx: Context | Runtime | None = None) -> dict[str, Any]:
    if isinstance(ctx, Context):
        runtime = ctx.inject(Runtime)
    else:
        runtime = ctx

    if runtime is not None:
        module = runtime.modules.get(obj.__module__)
        if module:
            return module.namespace

    return getattr(sys.modules.get(obj.__module__, None), '__dict__', {})


@contextmanager
def assert_exception(exc: type[Exception]):
    try:
        yield
    except exc:
        ...
    else:
        raise AssertionError(f"Expected {exc.__name__} to be raised.")