from dataclasses import dataclass, field, replace
from typing import Any, Callable, Iterable, List, Tuple, Union

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


def convert_literal(value: Any):
    literal = Literal.create(value)
    if type(literal.value) is Int:
        return ConstantScoreSource.create(literal.value.real)
    return literal


@dataclass(unsafe_hash=True, order=False)
class Operation(ExpressionNode):
    store: Tuple[Tuple[Source, str]] = field(default_factory=tuple, kw_only=True)


@dataclass(unsafe_hash=True, order=False)
class UnaryOperation(Operation):
    value: ExpressionNode

    def unroll(self) -> Iterable["Operation"]:
        *nodes, value = self.value.unroll()

        yield from nodes
        output = TempScoreSource.create()
        store = (output, "result")
        yield replace(self, value=value, store=(store,))
        yield output


@dataclass(unsafe_hash=True, order=False)
class BinaryOperation(Operation):
    former: GenericValue
    latter: GenericValue

    @classmethod
    def create(cls, former: GenericValue, latter: GenericValue, *args, **kwargs):
        """Factory method to create new operations"""

        if not isinstance(former, ExpressionNode):
            former = convert_literal(former)
        if not isinstance(latter, ExpressionNode):
            latter = convert_literal(latter)

        return super().create(former, latter, *args, **kwargs)


    def unroll(self) -> Iterable["Operation"]:
        *former_nodes, former_var = self.former.unroll()
        *latter_nodes, latter_var = self.latter.unroll()

        yield from former_nodes
        yield from latter_nodes

        if type(former_var) is TempScoreSource:
            temp_var = former_var
        else:
            temp_var = TempScoreSource.create()
            yield Set.create(temp_var, former_var)
        yield self.__class__.create(temp_var, latter_var)
        yield temp_var


class DataOperation(BinaryOperation):
    @classmethod
    def create(cls, former: DataSource, latter: GenericValue, *args, **kwargs):
        if not isinstance(latter, ExpressionNode):
            latter = Literal.create(latter)
        return super().create(former, latter, *args, **kwargs)


class Merge(DataOperation):
    def unroll(self):
        yield self


class MergeRoot(Merge):
    ...


@dataclass(unsafe_hash=True, order=False)
class Insert(DataOperation):
    index: int = 0

    def unroll(self):
        if type(self.latter) in (DataSource, Literal):
            yield self
        else:
            *latter_nodes, latter_var = self.latter.unroll()
            yield from latter_nodes
            yield self.__class__.create(self.former, 0, index=self.index)
            yield Set.create(self.former[self.index], latter_var)


class Append(Insert):
    @classmethod
    def create(cls, former: DataSource, latter: GenericValue, *args, **kwargs):
        return super().create(former, latter, index=-1)


class Prepend(Insert):
    @classmethod
    def create(cls, former: DataSource, latter: GenericValue, *args, **kwargs):
        return super().create(former, latter, index=0)


class Set(BinaryOperation):
    def unroll(self) -> Iterable["Operation"]:
        TempScoreSource.count = -1

        if type(self.latter) is DataSource:
            yield Set.create(self.former, self.latter)
        else:
            *latter_nodes, latter_var = self.latter.unroll()
            yield from latter_nodes
            yield Set.create(self.former, latter_var)


@ExpressionNode.link("add", reverse=True)
class Add(BinaryOperation):
    @classmethod
    def create(cls, former: GenericValue, latter: GenericValue):
        if not isinstance(former, Operation) and isinstance(latter, Operation):
            return super().create(latter, former)
        return super().create(former, latter)


@ExpressionNode.link("sub", reverse=True)
class Subtract(BinaryOperation):
    ...  # fmt: skip


@ExpressionNode.link("mul", reverse=True)
class Multiply(BinaryOperation):
    @classmethod
    def create(cls, former: GenericValue, latter: GenericValue):
        if not isinstance(former, Operation) and isinstance(latter, Operation):
            return super().create(latter, former)
        return super().create(former, latter)


@ExpressionNode.link("truediv", reverse=True)
class Divide(BinaryOperation):
    ...


@ExpressionNode.link("mod", reverse=True)
class Modulus(BinaryOperation):
    ...


@ExpressionNode.link("min", reverse=True)
class Min(BinaryOperation):
    ...


@ExpressionNode.link("max", reverse=True)
class Max(BinaryOperation):
    ...
