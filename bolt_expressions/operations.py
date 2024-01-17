from dataclasses import dataclass, field, replace
from typing import Any, Callable, ClassVar, Iterable, List, Tuple, Union, cast


from .optimizer import IrBinary, IrData, IrInsert, IrLiteral, IrOperation, IrScore, IrSource

from .literals import Literal
from .node import ExpressionNode
from .sources import (
    DataSource,
    ScoreSource,
    Source,
    TempScoreSource,
)

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

GenericValue = Union["Operation", ScoreSource, DataSource, Literal]


def wrapped_min(f, *args, **kwargs):
    values = args

    if len(args) == 1:
        if not isinstance(args[0], Iterable):
            return args[0]

        values = tuple(args[0])

    for i, node in enumerate(values):
        if not isinstance(node, ExpressionNode):
            continue

        remaining = values[:i] + values[i + 1 :]
        return Min.create(wrapped_min(f, *remaining, **kwargs), node)

    return f(*args, **kwargs)


def wrapped_max(f, *args, **kwargs):
    values = args

    if len(args) == 1:
        if not isinstance(args[0], Iterable):
            return args[0]

        values = tuple(args[0])

    for i, node in enumerate(values):
        if not isinstance(node, ExpressionNode):
            continue

        remaining = values[:i] + values[i + 1 :]
        return Max.create(wrapped_max(f, *remaining, **kwargs), node)

    return f(*args, **kwargs)


@dataclass(unsafe_hash=False, order=False)
class Operation(ExpressionNode):
    former: ExpressionNode
    latter: ExpressionNode
    store: Tuple[Source] = field(default_factory=tuple)

    op: ClassVar[str] = ""

    @classmethod
    def create(cls, former: Any, latter: Any, *args: Any, **kwargs: Any):
        """Factory method to create new operations"""

        if not isinstance(former, ExpressionNode):
            former = Literal.create(former)
        if not isinstance(latter, ExpressionNode):
            latter = Literal.create(latter)

        return super().create(former, latter, *args, **kwargs)

    def unroll(self) -> tuple[Iterable[IrOperation], IrSource]:
        former_nodes, former_value = self.former.unroll()
        latter_nodes, latter_value = self.latter.unroll()

        if isinstance(former_value, IrLiteral):
            node = replace(self, former=self.latter, latter=self.former)
            return node.unroll()

        operations: list[IrOperation] = [*former_nodes, *latter_nodes]

        if former_value.temp:
            temp_var = former_value
        else:
            t = TempScoreSource.create()
            temp_var = IrScore(holder=t.holder, obj=t.obj, temp=True)
            operations.append(IrBinary(op="set", left=temp_var, right=former_value))

        operations.append(IrBinary(op=self.op, left=temp_var, right=latter_value))

        return operations, temp_var


class DataOperation(Operation):
    def unroll(self):
        _, former_var = self.former.unroll()
        latter_nodes, latter_value = self.latter.unroll()

        if not isinstance(former_var, IrData):
            raise ValueError("Left side of data operation cannot be data source.")

        if isinstance(self, IrInsert):
            node = IrInsert(left=former_var, right=latter_value, index=self.index)
        else:
            node = IrBinary(op=self.op, left=former_var, right=latter_value)

        return (*latter_nodes, node), former_var


class Merge(DataOperation):
    op: ClassVar[str] = "merge"


class MergeRoot(Merge):
    op: ClassVar[str] = "merge"


@dataclass(unsafe_hash=False, order=False)
class Insert(DataOperation):
    op: ClassVar[str] = "insert"
    index: int = 0


class Append(Insert):
    op: ClassVar[str] = "append"

    @classmethod
    def create(cls, former: DataSource, latter: GenericValue, *args, **kwargs):
        return super().create(former, latter, index=-1)


class Prepend(Insert):
    op: ClassVar[str] = "prepend"

    @classmethod
    def create(cls, former: DataSource, latter: GenericValue, *args, **kwargs):
        return super().create(former, latter, index=0)


class Set(Operation):
    op: ClassVar[str] = "set"

    @classmethod
    def on_resolve(cls, callback: Callable):
        cls._resolve = callback

    def unroll(self):
        _, former_var = self.former.unroll()
        latter, latter_var = self.latter.unroll()

        if not isinstance(former_var, IrSource):
            raise ValueError("Left side of set operation cannot be literal.")

        op = IrBinary(op="set", left=former_var, right=latter_var)

        return (*latter, op), former_var

    def resolve(self):
        return self._resolve(self)


class ScoreOperation(Operation):
    ...


@ExpressionNode.link("add", reverse=True)
class Add(ScoreOperation):
    op: ClassVar[str] = "add"

    @classmethod
    def create(cls, former: GenericValue, latter: GenericValue):
        if not isinstance(former, Operation) and isinstance(latter, Operation):
            return super().create(latter, former)
        return super().create(former, latter)


@ExpressionNode.link("sub", reverse=True)
class Subtract(ScoreOperation):
    op: ClassVar[str] = "sub"


@ExpressionNode.link("mul", reverse=True)
class Multiply(ScoreOperation):
    op: ClassVar[str] = "mul"

    @classmethod
    def create(cls, former: GenericValue, latter: GenericValue):
        if not isinstance(former, Operation) and isinstance(latter, Operation):
            return super().create(latter, former)
        return super().create(former, latter)


@ExpressionNode.link("truediv", reverse=True)
class Divide(ScoreOperation):
    op: ClassVar[str] = "div"


@ExpressionNode.link("mod", reverse=True)
class Modulus(ScoreOperation):
    op: ClassVar[str] = "mod"


@ExpressionNode.link("min", reverse=True)
class Min(ScoreOperation):
    op: ClassVar[str] = "min"


@ExpressionNode.link("max", reverse=True)
class Max(ScoreOperation):
    op: ClassVar[str] = "max"


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
