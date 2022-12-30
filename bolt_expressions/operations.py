from dataclasses import dataclass, field
from typing import Any, Callable, Iterable, List, Tuple, Union

from nbtlib import Int

from .literals import Literal
from .node import ExpressionNode
from .sources import ConstantScoreSource, DataSource, Source, TempScoreSource

# from rich import print
# from rich.pretty import pprint

__all__ = [
    "Operation",
    "DataOperation",
    "Merge",
    "MergeRoot",
    "Insert",
    "Append",
    "Prepend",
    "Set",
    "Add",
    "Subtract",
    "Multiply",
    "Divide",
    "Modulus",
    "Min",
    "Max",
    "wrapped_min",
    "wrapped_max",
]

GenericValue = Union["Operation", "Source", int, str]


def wrapped_min(f, *args, **kwargs):
    if len(args) == 1:
        value = args[0]

        if not isinstance(value, Iterable):
            return value

        args = tuple(value)

    for i, node in enumerate(args):
        if not isinstance(node, ExpressionNode):
            continue

        remaining = args[:i] + args[i + 1 :]
        return Min.create(wrapped_min(f, *remaining, **kwargs), node)

    return f(*args, **kwargs)


def wrapped_max(f, *args, **kwargs):
    if len(args) == 1:
        value = args[0]

        if not isinstance(value, Iterable):
            return value

        args = tuple(value)

    for i, node in enumerate(args):
        if not isinstance(node, ExpressionNode):
            continue

        remaining = args[:i] + args[i + 1 :]
        return Max.create(wrapped_max(f, *remaining, **kwargs), node)

    return f(*args, **kwargs)


@dataclass(unsafe_hash=False, order=False)
class Operation(ExpressionNode):
    former: GenericValue
    latter: GenericValue
    store: Tuple[Source] = field(default_factory=tuple)

    @classmethod
    def create(cls, former: GenericValue, latter: GenericValue, *args, **kwargs):
        """Factory method to create new operations"""

        if not isinstance(former, ExpressionNode):
            former = Literal.create(former)
        if not isinstance(latter, ExpressionNode):
            latter = Literal.create(latter)

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


class DataOperation(Operation):
    ...


class Merge(DataOperation):
    def unroll(self):
        yield self


class MergeRoot(Merge):
    ...


@dataclass(unsafe_hash=False, order=False)
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


class ScoreOperation(Operation):
    ...


@ExpressionNode.link("add", reverse=True)
class Add(ScoreOperation):
    @classmethod
    def create(cls, former: GenericValue, latter: GenericValue):
        if not isinstance(former, Operation) and isinstance(latter, Operation):
            return super().create(latter, former)
        return super().create(former, latter)


@ExpressionNode.link("sub", reverse=True)
class Subtract(ScoreOperation):
    ...  # fmt: skip


@ExpressionNode.link("mul", reverse=True)
class Multiply(ScoreOperation):
    @classmethod
    def create(cls, former: GenericValue, latter: GenericValue):
        if not isinstance(former, Operation) and isinstance(latter, Operation):
            return super().create(latter, former)
        return super().create(former, latter)


@ExpressionNode.link("truediv", reverse=True)
class Divide(ScoreOperation):
    ...


@ExpressionNode.link("mod", reverse=True)
class Modulus(ScoreOperation):
    ...


@ExpressionNode.link("min", reverse=True)
class Min(ScoreOperation):
    ...


@ExpressionNode.link("max", reverse=True)
class Max(ScoreOperation):
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
