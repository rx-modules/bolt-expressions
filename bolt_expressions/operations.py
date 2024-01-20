from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any, Callable, ClassVar, Iterable, Type, TypeVar, Union, overload
import typing as t

from bolt_expressions.optimizer import IrBinary, IrLiteral, IrSource

from .optimizer import (
    IrBinary,
    IrData,
    IrInsert,
    IrLiteral,
    IrOperation,
    IrScore,
    IrSource,
    IrUnary,
)
from .node import ExpressionNode
from .literals import convert_node


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

T = TypeVar("T")
def wrapped_min(f: Any, *args: T, **kwargs: Any) -> Union[T, "Min"]:
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
        return Min(
            former=wrapped_min(f, *remaining, **kwargs),
            latter=node,
            ctx=node.ctx,
            proxied=get_proxied_type(node),
        )

    return f(*args, **kwargs)


def wrapped_max(f: Any, *args: T, **kwargs: Any) -> Union[T, "Max"]:
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
        return Max(
            former=wrapped_max(f, *remaining, **kwargs),
            latter=node,
            ctx=node.ctx,
            proxied=get_proxied_type(node),
        )

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
    proxied: Any = field(default=None, repr=False)
    proxied_attributes: ClassVar[list[str]] = []

    def __init_subclass__(cls) -> None:
        for operator in cls.proxied_attributes:
            setattr(cls, operator, OperatorProxyDescriptor("proxied", operator))


def unwrap_proxy(obj: Any) -> Any:
    if not isinstance(obj, OperatorProxy):
        return obj
    return unwrap_proxy(obj.proxied)

def get_proxied_type(obj: Any) -> type:
    unwrapped = unwrap_proxy(obj)

    if isinstance(unwrapped, type):
        return unwrapped

    return type(unwrapped) 


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
            type, target, path, _ = self.expr.temp_data()
            return IrData(type=type, target=target, path=path, temp=True)

        holder, obj = self.expr.temp_score()
        return IrScore(holder=holder, obj=obj, temp=True)


@dataclass(unsafe_hash=False, order=False)
class UnaryOperation(Operation):
    target: ExpressionNode

    def create_operation(self, target: IrSource) -> IrUnary:
        return IrUnary(op=self.op, target=target)

    def unroll(self) -> tuple[Iterable[IrOperation], IrSource]:
        target = convert_node(self.target, self.ctx)
        target_nodes, target_value = target.unroll()

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


UnaryOpFunction = Callable[[ExpressionNode], T]

@overload
def unary_operator(
    cls: Type[UnaryOp],
) -> UnaryOpFunction[UnaryOp]:
    ...

@overload
def unary_operator(
    cls: Type[UnaryOp],
    result: Callable[[UnaryOp], T],
) -> UnaryOpFunction[T]:
    ...

def unary_operator(
    cls: Type[UnaryOp],
    result: Callable[[UnaryOp], T] | None = None,
) -> UnaryOpFunction[UnaryOp | T | None]:
    def decorator(target: ExpressionNode):
        obj = cls(target=target, ctx=target.ctx, proxied=get_proxied_type(target))
        return result(obj) if result else obj

    return decorator


@dataclass(unsafe_hash=False, order=False)
class BinaryOperation(Operation):
    former: ExpressionNode
    latter: Any

    def create_operation(self, left: IrSource, right: IrSource | IrLiteral) -> IrBinary:
        return IrBinary(op=self.op, left=left, right=right)

    def unroll(self) -> tuple[Iterable[IrOperation], IrSource]:
        former = convert_node(self.former, self.ctx)
        latter = convert_node(self.latter, self.ctx)

        former_nodes, former_value = former.unroll()
        latter_nodes, latter_value = latter.unroll()

        operations: list[IrOperation] = [*former_nodes, *latter_nodes]

        if self.in_place and isinstance(former_value, IrSource):
            temp_var = former_value
        else:
            temp_var = self._create_temporary()
            operations.append(IrBinary(op="set", left=temp_var, right=former_value))

        operation = self.create_operation(temp_var, latter_value)
        operations.append(operation)

        return operations, temp_var


BinOp = TypeVar("BinOp", bound=BinaryOperation)

BinaryOpFunction = Callable[[ExpressionNode, Any], T]

SanitizedBinaryOpFunction = Callable[[ExpressionNode, ExpressionNode], T]


def sanitized(f: SanitizedBinaryOpFunction[T]) -> BinaryOpFunction[T]:
    def decorated(node: ExpressionNode, value: Any):        
        return f(node, convert_node(value, node.ctx))

    return decorated


@overload
def binary_operator(
    cls: Type[BinOp],
    *,
    result: None = None,
) -> BinaryOpFunction[BinOp]:
    ...

@overload
def binary_operator(
    cls: Type[BinOp],
    *,
    result: Callable[[BinOp], T],
) -> BinaryOpFunction[T]:
    ...

@overload
def binary_operator(
    cls: Type[BinOp],
    *,
    reverse: t.Literal[True],
) -> tuple[BinaryOpFunction[BinOp], BinaryOpFunction[BinOp]]:
    ...

@overload
def binary_operator(
    cls: Type[BinOp],
    *,
    reverse: t.Literal[True],
    result: Callable[[BinOp], T],
) -> tuple[BinaryOpFunction[T], BinaryOpFunction[T]]:
    ...

def binary_operator(
    cls: Type[BinOp],
    *,
    reverse: bool = False,
    result: Callable[[BinOp], T] | None = None
) -> BinaryOpFunction[T | BinOp] | tuple[BinaryOpFunction[T | BinOp], BinaryOpFunction[T | BinOp]]:
    @sanitized
    def decorator(left: ExpressionNode, right: ExpressionNode) -> T | BinOp:
        obj = cls(former=left, latter=right, ctx=left.ctx, proxied=get_proxied_type(left))
        return result(obj) if result else obj

    if not reverse:
        return decorator

    @sanitized
    def reversed(right: ExpressionNode, left: ExpressionNode) -> T | BinOp:
        obj = cls(former=left, latter=right, ctx=right.ctx, proxied=get_proxied_type(right))
        return result(obj) if result else obj

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

