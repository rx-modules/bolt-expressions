from dataclasses import dataclass
from typing import Any, Callable, Iterable, List, Union

from nbtlib import Int

from .literals import Literal
from .node import ExpressionNode
from .sources import ConstantScoreSource, DataSource, Source, TempScoreSource

# from rich import print
# from rich.pretty import pprint


GenericValue = Union["Operation", "Source", int, str]


def wrapped_min(*args, **kwargs):
    if isinstance(args[0], ExpressionNode):
        return args[0].__min__(args[1])
    elif isinstance(args[1], ExpressionNode):
        return args[1].__rmin__(args[0])
    return min(*args, *kwargs)


def wrapped_max(*args, **kwargs):
    if isinstance(args[0], ExpressionNode):
        return args[0].__max__(args[1])
    elif isinstance(args[1], ExpressionNode):
        return args[1].__rmax__(args[0])
    return min(*args, *kwargs)


@dataclass(unsafe_hash=False, order=False)
class Operation(ExpressionNode):
    former: GenericValue
    latter: GenericValue

    @classmethod
    def create(cls, former: GenericValue, latter: GenericValue):
        """Factory method to create new operations"""

        if not isinstance(former, ExpressionNode):
            former = cls._handle_literal(former)
        if not isinstance(latter, ExpressionNode):
            latter = cls._handle_literal(latter)

        return super().create(former, latter)

    @classmethod
    def _handle_literal(cls, value: Any):
        literal = Literal.create(value)
        if type(literal.value) is Int:
            return ConstantScoreSource.create(literal.value.real)
        return literal

    def unroll(self) -> Iterable["Operation"]:
        *former_nodes, former_var = self.former.unroll()
        *latter_nodes, latter_var = self.latter.unroll()

        yield from former_nodes
        yield from latter_nodes

        temp_var = TempScoreSource.create()
        yield Set.create(temp_var, former_var)
        yield self.__class__.create(temp_var, latter_var)
        yield temp_var


class Set(Operation):
    @classmethod
    def on_resolve(cls, callback: Callable):
        cls._resolve = callback

    def unroll(self) -> Iterable["Operation"]:
        TempScoreSource.count = -1

        if type(self.latter) is DataSource:
            yield Set.create(self.former, self.latter)
        else:
            *latter_nodes, latter_var = self.latter.unroll()
            yield from latter_nodes
            yield Set.create(self.former, latter_var)

    def resolve(self):
        return self._resolve(self)


@ExpressionNode.link("add", reverse=True)
class Add(Operation):
    @classmethod
    def create(cls, former: GenericValue, latter: GenericValue):
        if not isinstance(former, Operation) and isinstance(latter, Operation):
            return super().create(latter, former)
        return super().create(former, latter)


@ExpressionNode.link("sub", reverse=True)
class Subtract(Operation):
    ...  # fmt: skip


@ExpressionNode.link("mul", reverse=True)
class Multiply(Operation):
    @classmethod
    def create(cls, former: GenericValue, latter: GenericValue):
        if not isinstance(former, Operation) and isinstance(latter, Operation):
            return super().create(latter, former)
        return super().create(former, latter)


@ExpressionNode.link("truediv", reverse=True)
class Divide(Operation):
    ...


@ExpressionNode.link("mod", reverse=True)
class Modulus(Operation):
    ...


@ExpressionNode.link("min", reverse=True)
class Min(Operation):
    ...


@ExpressionNode.link("max", reverse=True)
class Max(Operation):
    ...


@ExpressionNode.link("if")
class If(Operation):
    ...


# @ExpressionNode.link("eq")
# class Equal(Operation): ...


# @ExpressionNode.link("ne")
# class NotEqual(Operation): ...


@ExpressionNode.link("lt")
class LessThan(Operation):
    ...


@ExpressionNode.link("gt")
class GreaterThan(Operation):
    ...


@ExpressionNode.link("le")
class LessThanOrEqualTo(Operation):
    ...


@ExpressionNode.link("ge")
class GreaterThanOrEqualTo(Operation):
    ...


@ExpressionNode.link("abs")
class Abs(Operation):
    @classmethod
    def create(cls, former: GenericValue):
        return If.create(LessThan.create(former, 0), Multiply.create(former, -1))


# def __neg__(self):
#     return Multiply.create(self, -1)

# def __pos__(self):
#     return self

# def __abs__(self):
#     return If.create(LessThan.create(self, 0), Multiply.create(self, -1))
