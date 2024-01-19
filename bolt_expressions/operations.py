from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any, Callable, ClassVar, Iterable, Type, TypeVar, overload
import typing as t

from beet import Context

from bolt_expressions.optimizer import IrBinary, IrLiteral, IrSource

from .utils import type_name


from .optimizer import (
    IrBinary,
    IrData,
    IrInsert,
    IrLiteral,
    IrOperation,
    IrScore,
    IrSource,
    IrUnary,
    NbtType,
)
from .node import Expression, ExpressionNode
from .literals import Literal, convert_node


__all__ = [
    "wrapped_min",
    "wrapped_max",
    "OperatorProxyDescriptor",
    "OperatorProxy",
    "ResultType",
    "Operation",
    "UnaryOperation",
    "unary_operator",
    "BinaryOperation",
    "binary_operator",
    "Remove",
    "Merge",
    "InPlaceMerge",
    "Insert",
    "Append",
    "Prepend",
    "Set",
    "Enable",
    "Reset",
    "Add",
    "Subtract",
    "Multiply",
    "Divide",
    "Modulus",
    "Min",
    "Max",
]


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


@dataclass
class OperatorProxyDescriptor:
    target_name: str
    operator: str
    
    def __get__(self, obj: Any, objtype: Any = None):
        if obj is None:
            attr = getattr(objtype, self.target_name, None)
            if attr is None:
                return self

            return getattr(attr, self.operator)

        attr = getattr(obj, self.target_name)
        attr_cls = attr if isinstance(attr, type) else type(attr)

        f = getattr(attr_cls, self.operator)
        return f.__get__(obj, objtype)

@dataclass(kw_only=True)
class OperatorProxy:
    proxied: Any = None
    proxied_attributes: ClassVar[list[str]] = []

    def __init_subclass__(cls) -> None:
        for operator in cls.proxied_attributes:
            setattr(cls, operator, OperatorProxyDescriptor("proxied", operator))



class ResultType(Enum):
    score = auto()
    data = auto()

@dataclass(unsafe_hash=False, order=False, kw_only=True)
class Operation(ExpressionNode, OperatorProxy):
    in_place: ClassVar[bool] = False
    op: ClassVar[str] = ""
    result: ClassVar[ResultType] = ResultType.score

    proxied_attributes: ClassVar[list[str]] = [
        "__add__",
        "__radd__",
        "__sub__",
        "__rsub__",
        "__mul__",
        "__rmul__",
        "__truediv__",
        "__rtruediv__",
        "__mod__",
        "__rmod__",
        "__pow__",
        "__neg__",
        "__pos__",
        "__lshift__",
        "__rshift__",
        "__or__",
        "__ror__",
        "__xor__",
        "__rxor__",
        "__and__",
        "__rand__",
        "__invert__",
        "__le__",
        "__lt__",
        "__eq__",
        "__ne__",
        "__ge__",
        "__gt__",
        "__iter__",
        "__len__",
        "__contains__",
    ]

    def _create_temporary(self):
        if self.result == ResultType.data:
            type, target, path = self.expr.temp_data()
            return IrData(type=type, target=target, path=path, temp=True)

        holder, obj = self.expr.temp_score()
        return IrScore(holder=holder, obj=obj, temp=True)


@dataclass(unsafe_hash=False, order=False)
class UnaryOperation(Operation):
    target: ExpressionNode

    def create_operation(self, target: IrSource) -> IrUnary:
        return IrUnary(op=self.op, target=target)

    def unroll(self) -> tuple[Iterable[IrOperation], IrSource]:
        target_nodes, target_value = self.target.unroll()

        if not isinstance(target_value, IrSource):
            raise ValueError("Left operand must be a source node.")

        operations: list[IrOperation] = [*target_nodes]

        print(self, self.in_place)
        if self.in_place:
            temp_var = target_value
        else:
            temp_var = self._create_temporary()
            operations.append(IrBinary(op="set", left=temp_var, right=target_value))

        operation = self.create_operation(temp_var)
        operations.append(operation)

        return operations, temp_var


UnaryOp = TypeVar("UnaryOp", bound=UnaryOperation)

UnaryOpFunction = Callable[[ExpressionNode], UnaryOp]

def unary_operator(cls: Type[UnaryOp]) -> UnaryOpFunction[UnaryOp]:
    def decorator(target: ExpressionNode):
        return cls(target=target, ctx=target.ctx, proxied=type(target))

    return decorator


@dataclass(unsafe_hash=False, order=False)
class BinaryOperation(Operation):
    former: ExpressionNode
    latter: Any

    def create_operation(self, left: IrSource, right: IrSource | IrLiteral) -> IrBinary:
        return IrBinary(op=self.op, left=left, right=right)

    def unroll(self) -> tuple[Iterable[IrOperation], IrSource]:
        latter = convert_node(self.latter, self.ctx)

        former_nodes, former_value = self.former.unroll()
        latter_nodes, latter_value = latter.unroll()

        if not isinstance(former_value, IrSource):
            raise ValueError("Left operand must be a source node.")

        operations: list[IrOperation] = [*former_nodes, *latter_nodes]

        if self.in_place:
            temp_var = former_value
        else:
            temp_var = self._create_temporary()
            operations.append(IrBinary(op="set", left=temp_var, right=former_value))

        operation = self.create_operation(temp_var, latter_value)
        operations.append(operation)

        return operations, temp_var


BinOp = TypeVar("BinOp", bound=BinaryOperation)

BinaryOpFunction = Callable[[ExpressionNode, Any], BinOp | None]

SanitizedBinaryOpFunction = Callable[[ExpressionNode, ExpressionNode], BinOp | None]


def sanitized(f: SanitizedBinaryOpFunction[BinOp]) -> BinaryOpFunction[BinOp]:
    def decorated(node: ExpressionNode, value: Any):        
        return f(node, convert_node(value, node.ctx))

    return decorated


@overload
def binary_operator(cls: Type[BinOp], *, immediate: bool = False) -> BinaryOpFunction[BinOp]:
    ...

@overload
def binary_operator(
    cls: Type[BinOp], *, reverse: t.Literal[True], immediate: bool = False
) -> tuple[BinaryOpFunction[BinOp], BinaryOpFunction[BinOp]]:
    ...

def binary_operator(
    cls: Type[BinOp],
    *,
    reverse: bool = False,
    immediate: bool = False,
) -> BinaryOpFunction[BinOp] | tuple[BinaryOpFunction[BinOp], BinaryOpFunction[BinOp]]:
    @sanitized
    def decorator(left: ExpressionNode, right: ExpressionNode):
        obj = cls(former=left, latter=right, ctx=left.ctx, proxied=type(left))

        if immediate:
            left.expr.resolve(obj)
            return
            
        return obj

    if not reverse:
        return decorator

    @sanitized
    def reversed(right: ExpressionNode, left: ExpressionNode):
        obj = cls(former=left, latter=right, ctx=right.ctx, proxied=type(right))

        if immediate:
            left.expr.resolve(obj)
            return

        return obj

    return (decorator, reversed)


class Remove(UnaryOperation):
    op: ClassVar[str] = "remove"
    in_place: ClassVar[bool] = True


class Merge(BinaryOperation):
    op: ClassVar[str] = "merge"
    result: ClassVar[ResultType] = ResultType.data

class InPlaceMerge(BinaryOperation):
    op: ClassVar[str] = "merge"
    in_place: ClassVar[bool] = True


@dataclass(eq=False, order=False)
class Insert(BinaryOperation):
    op: ClassVar[str] = "insert"
    in_place: ClassVar[bool] = True

    index: int = 0

    def create_operation(self, left: IrSource, right: IrSource | IrLiteral) -> IrInsert:
        return IrInsert(left=left, right=right, index=self.index)


class Append(BinaryOperation):
    op: ClassVar[str] = "append"
    in_place: ClassVar[bool] = True


class Prepend(BinaryOperation):
    op: ClassVar[str] = "prepend"
    in_place: ClassVar[bool] = True


class Set(BinaryOperation):
    op: ClassVar[str] = "set"
    in_place: ClassVar[bool] = True


class Enable(UnaryOperation):
    op: ClassVar[str] = "enable"
    in_place: ClassVar[bool] = True


class Reset(UnaryOperation):
    op: ClassVar[str] = "reset"
    in_place: ClassVar[bool] = True


class Add(BinaryOperation):
    op: ClassVar[str] = "add"


class Subtract(BinaryOperation):
    op: ClassVar[str] = "sub"


class Multiply(BinaryOperation):
    op: ClassVar[str] = "mul"


class Divide(BinaryOperation):
    op: ClassVar[str] = "div"


class Modulus(BinaryOperation):
    op: ClassVar[str] = "mod"


class Min(BinaryOperation):
    op: ClassVar[str] = "min"


class Max(BinaryOperation):
    op: ClassVar[str] = "max"

