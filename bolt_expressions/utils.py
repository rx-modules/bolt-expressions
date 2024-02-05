from contextlib import contextmanager
import sys
from types import NoneType
from typing import Any, Dict, _UnionGenericAlias, is_typeddict  # type: ignore
from bolt import Runtime
from nbtlib import Base  # type: ignore
from beet import Context

__all__ = [
    "type_name",
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

    return getattr(sys.modules.get(obj.__module__, None), "__dict__", {})


@contextmanager
def assert_exception(exc: type[Exception]):
    try:
        yield
    except exc:
        ...
    else:
        raise AssertionError(f"Expected {exc.__name__} to be raised.")
