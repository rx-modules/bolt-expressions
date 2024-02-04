from typing import Any, Iterable, TypeVar, Union

from .sources import binary_operator
from .operations import Min, Max

from .node import ExpressionNode

T = TypeVar("T")

binary_min = binary_operator(Min)
binary_max = binary_operator(Max)


def wrapped_min(f: Any, *args: T, **kwargs: Any) -> Union[T, Any]:
    values = args

    if len(args) == 1:
        if isinstance(args[0], ExpressionNode):
            return args[0]
        if not isinstance(args[0], Iterable):
            return args[0]

        values = tuple(args[0])

    for i, node in enumerate(values):
        if not isinstance(node, ExpressionNode):
            continue

        remaining = values[:i] + values[i + 1 :]
        return binary_min(node, wrapped_min(f, *remaining, **kwargs))

    return f(*args, **kwargs)


def wrapped_max(f: Any, *args: T, **kwargs: Any) -> Union[T, Any]:
    values = args

    if len(args) == 1:
        if isinstance(args[0], ExpressionNode):
            return args[0]
        if not isinstance(args[0], Iterable):
            return args[0]

        values = tuple(args[0])

    for i, node in enumerate(values):
        if not isinstance(node, ExpressionNode):
            continue

        remaining = values[:i] + values[i + 1 :]
        return binary_max(node, wrapped_max(f, *remaining, **kwargs))

    return f(*args, **kwargs)
