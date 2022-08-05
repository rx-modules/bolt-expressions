from dataclasses import dataclass, field
from functools import cache, partial
from typing import Any, Callable, Iterable, Optional, Set, Type, overload


MethodDict = dict[str, Callable[..., Any]]


@dataclass
class ExpressionMethods:
    methods: dict[Type["ExpressionNode"], MethodDict] = field(default_factory=dict)

    def add(self, node_type: Type["ExpressionNode"], **methods: MethodDict):
        self.methods.setdefault(node_type, {}).update(methods)

    def get(self, node_type: Type["ExpressionNode"], method_name: str):
        for type, methods in self.methods.items():
            if issubclass(node_type, type) and method_name in methods:
                return methods[method_name]


@dataclass(unsafe_hash=True, eq=False, kw_only=True)
class ExpressionNode:
    methods: ExpressionMethods = field(default=None, hash=False, repr=False)

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
    def create(cls, *args, **kwargs):
        kwargs["methods"] = cls.resolve_context(*args, **kwargs)
        return cls(*args, **kwargs)

    @staticmethod
    def resolve_context(*args, **kwargs):
        if context := kwargs.get("methods"):
            return context
        for node in (*args, *kwargs.values()):
            if isinstance(node, ExpressionNode) and node.methods:
                return node.methods

    @cache
    def __getattr__(self, key: str):
        if self.methods and (method := self.methods.get(type(self), key)):
            return partial(method, self)
        raise AttributeError(f"'{type(self).__name__}' object has no method '{key}'.")

    def emit(self, method_name: str, *args, **kwargs):
        method = self.__getattr__(method_name)
        return method(*args, **kwargs)

    def unroll(self):
        yield self
