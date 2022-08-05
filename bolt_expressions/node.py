from dataclasses import dataclass, field
from typing import Callable, Iterable, Optional, Set, overload


@dataclass(unsafe_hash=True, order=False, eq=False)
class ExpressionNode:
    attached_methods = set()

    @classmethod
    def link(cls, name: str, reverse=False, unary=False):
        def decorator(operation):
            is_class = isinstance(operation, type) and issubclass(
                operation, ExpressionNode
            )
            create = operation.create if is_class else operation

            def unary_method(node: "ExpressionNode"):
                return create(node)

            def binary_method(left: "ExpressionNode", right: "ExpressionNode"):
                return create(left, right)

            def rbinary_method(left: "ExpressionNode", right: "ExpressionNode"):
                return create(right, left)

            setattr(cls, f"__{name}__", unary_method if unary else binary_method)
            if reverse and not unary:
                setattr(cls, f"__r{name}__", rbinary_method)
            return operation

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
    def create(cls, *args, **kwargs):
        return cls(*args, **kwargs)

    def unroll(self):
        yield self
