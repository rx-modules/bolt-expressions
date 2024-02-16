from abc import ABC, abstractmethod
from dataclasses import dataclass, replace
from typing import Any, ClassVar, Iterable

from bolt_expressions.optimizer import IrOperation, IrSource

from .typing import NbtType
from .optimizer import (
    IrBinary,
    IrBinaryCondition,
    IrCast,
    IrCondition,
    IrData,
    IrInsert,
    IrLiteral,
    IrNode,
    IrOperation,
    IrScore,
    IrSet,
    IrSource,
    IrUnary,
    IrUnaryCondition,
)
from .node import ExpressionNode, ResultType, UnrollHelper
from .literals import convert_node


__all__ = [
    "ResultType",
    "Operation",
    "UnaryOperation",
    "BinaryOperation",
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


@dataclass(unsafe_hash=False, order=False, kw_only=True)
class Operation(ExpressionNode, ABC):
    in_place: ClassVar[bool] = False
    commutative: ClassVar[bool] = False
    op: ClassVar[str] = ""
    result: ClassVar[ResultType] = ResultType.score

    @property
    @abstractmethod
    def in_place_target(self) -> ExpressionNode | None:
        ...


@dataclass(unsafe_hash=False, order=False)
class UnaryOperation(Operation):
    target: ExpressionNode

    @property
    def in_place_target(self) -> ExpressionNode | None:
        if not self.in_place:
            return None

        return self.target

    def create_operation(self, target: IrSource) -> IrUnary:
        return IrUnary(op=self.op, target=target)

    def unroll(self, helper: UnrollHelper) -> tuple[Iterable[IrOperation], IrSource]:
        target = convert_node(self.target, self.ctx)
        target_nodes, target_value = target.unroll(helper)

        if not isinstance(target_value, IrSource):
            raise ValueError("Operand must be a source node.")

        operations: list[IrOperation] = [*target_nodes]

        if self.in_place:
            temp_var = target_value
        else:
            temp_var = helper.create_temporary(self.result)
            operations.append(IrSet(left=temp_var, right=target_value))

        operation = self.create_operation(temp_var)
        operations.append(operation)

        return operations, temp_var


def balance_priority(node: IrNode, helper: UnrollHelper) -> int:
    if isinstance(node, IrSource) and node.to_tuple() in helper.temporaries:
        return 3

    if isinstance(node, IrData):
        return 2

    if isinstance(node, IrScore):
        return 1

    return 0


@dataclass(unsafe_hash=False, order=False)
class BinaryOperation(Operation):
    former: ExpressionNode
    latter: Any

    @property
    def in_place_target(self) -> ExpressionNode | None:
        if not self.in_place:
            return None

        return self.former

    def create_operation(self, left: IrSource, right: IrSource | IrLiteral) -> IrBinary:
        return IrBinary(op=self.op, left=left, right=right)

    def unroll(self, helper: UnrollHelper) -> tuple[Iterable[IrOperation], IrSource]:
        former = convert_node(self.former, self.ctx)
        latter = convert_node(self.latter, self.ctx)

        former_nodes, former_value = former.unroll(helper)
        latter_nodes, latter_value = latter.unroll(helper)

        if self.commutative:
            former_priority = balance_priority(former_value, helper)
            latter_priority = balance_priority(latter_value, helper)

            if former_priority < latter_priority:
                node = replace(self, former=latter, latter=former)
                return node.unroll(helper)

        operations: list[IrOperation] = [*former_nodes, *latter_nodes]

        if self.in_place and isinstance(former_value, IrSource):
            temp_var = former_value
        else:
            temp_var = helper.create_temporary(self.result)
            operations.append(IrSet(left=temp_var, right=former_value))

        operation = self.create_operation(temp_var, latter_value)
        operations.append(operation)

        return operations, temp_var


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

    def create_operation(
        self, left: IrSource, right: IrSource | IrLiteral | IrCondition
    ) -> IrInsert:
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

    def create_operation(
        self, left: IrSource, right: IrSource | IrLiteral | IrCondition
    ) -> IrSet:
        return IrSet(left=left, right=right)


@dataclass(eq=False, order=False)
class Cast(BinaryOperation):
    op: ClassVar[str] = "cast"
    in_place: ClassVar[bool] = True

    cast_type: NbtType = Any

    def create_operation(
        self, left: IrSource, right: IrSource | IrLiteral | IrCondition
    ) -> IrCast:
        return IrCast(left=left, right=right, cast_type=self.cast_type)


class Enable(UnaryOperation):
    op: ClassVar[str] = "enable"
    in_place: ClassVar[bool] = True


class Reset(UnaryOperation):
    op: ClassVar[str] = "reset"
    in_place: ClassVar[bool] = True


class Add(BinaryOperation):
    op: ClassVar[str] = "add"
    commutative: ClassVar[bool] = True


class Subtract(BinaryOperation):
    op: ClassVar[str] = "sub"


class Multiply(BinaryOperation):
    op: ClassVar[str] = "mul"
    commutative: ClassVar[bool] = True


class Divide(BinaryOperation):
    op: ClassVar[str] = "div"


class Modulus(BinaryOperation):
    op: ClassVar[str] = "mod"


class Min(BinaryOperation):
    op: ClassVar[str] = "min"
    commutative: ClassVar[bool] = True


class Max(BinaryOperation):
    op: ClassVar[str] = "max"
    commutative: ClassVar[bool] = True


class UnaryCondition(UnaryOperation):
    negated: ClassVar[bool] = False

    def unroll(self, helper: UnrollHelper) -> tuple[Iterable[IrOperation], IrSource]:
        target_nodes, target_var = convert_node(self.target, self.ctx).unroll(helper)

        if not isinstance(target_var, IrSource):
            raise ValueError("Operand must be a source node.")

        condition = IrUnaryCondition(
            op=self.op, target=target_var, negated=self.negated
        )
        temp_var = helper.create_temporary(ResultType.score)
        op = IrSet(left=temp_var, right=condition)

        return (*target_nodes, op), temp_var


@dataclass
class BinaryCondition(BinaryOperation):
    negated: ClassVar[bool] = False

    def unroll(self, helper: UnrollHelper) -> tuple[Iterable[IrOperation], IrSource]:
        former_nodes, former_var = convert_node(self.former, self.ctx).unroll(helper)
        latter_nodes, latter_var = convert_node(self.latter, self.ctx).unroll(helper)

        temp_var = helper.create_temporary(ResultType.score)
        condition = IrBinaryCondition(
            op=self.op, left=former_var, right=latter_var, negated=self.negated
        )
        op = IrSet(left=temp_var, right=condition)

        return (*former_nodes, *latter_nodes, op), temp_var


class Boolean(UnaryCondition):
    op: ClassVar[str] = "boolean"


class Not(UnaryCondition):
    op: ClassVar[str] = "boolean"
    negated: ClassVar[bool] = True


class LessThan(BinaryCondition):
    op: ClassVar[str] = "less_than"


class LessThanOrEqualTo(BinaryCondition):
    op: ClassVar[str] = "less_than_or_equal_to"


class GreaterThan(BinaryCondition):
    op: ClassVar[str] = "greater_than"


class GreaterThanOrEqualTo(BinaryCondition):
    op: ClassVar[str] = "greater_than_or_equal_to"


class Equal(BinaryCondition):
    op: ClassVar[str] = "equal"


class NotEqual(BinaryCondition):
    op: ClassVar[str] = "equal"
    negated: ClassVar[bool] = True
