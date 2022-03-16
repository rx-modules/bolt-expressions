from dataclasses import dataclass
from typing import Iterable, overload


@dataclass(unsafe_hash=True, order=False, eq=False)
class ExpressionNode:
    @classmethod
    def link(cls, magic_method: str, reverse=False):
        def decorator(operation_class):
            def normal(self, other: "ExpressionNode"):
                return operation_class.create(self, other)

            def reversed(self, other: "ExpressionNode"):
                return operation_class.create(other, self)

            setattr(cls, f"__{magic_method}__", normal if not reverse else reversed)
            return operation_class

        return decorator

    @classmethod
    def create(cls, *args, **kwargs):
        return cls(*args, **kwargs)

    def unroll(self):
        yield self