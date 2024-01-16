from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Callable, Iterable, Optional, Set, overload

from .optimizer import IrLiteral, IrOperation, IrSource

__all__ = [
    "ExpressionNode",
]


@dataclass(unsafe_hash=True, order=False, eq=False)
class ExpressionNode(ABC):
    attached_methods = set()

    @classmethod
    def link(cls, magic_method: str, reverse=False):
        def decorator(operation_class):
            def normal(self, other: "ExpressionNode"):
                return operation_class.create(self, other)

            def reversed(self, other: "ExpressionNode"):
                return operation_class.create(other, self)

            setattr(cls, f"__{magic_method}__", normal)
            if reverse:
                setattr(cls, f"__r{magic_method}__", reversed)
            return operation_class

        return decorator

    @classmethod
    def attach(cls, method_name: str, function: Callable):
        """Attach a method to an expression node."""
        if getattr(cls, method_name, None) and method_name not in cls.attached_methods:
            return

        def method(self, *args, **kwargs):
            return function(self, *args, **kwargs)

        setattr(cls, method_name, method)
        cls.attached_methods.add(method_name)

    @classmethod
    def create(cls, *args: Any, **kwargs: Any):
        return cls(*args, **kwargs)

    @abstractmethod
    def unroll(self) -> tuple[Iterable[IrOperation], IrSource | IrLiteral]:
        ...
