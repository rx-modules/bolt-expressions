from contextlib import contextmanager
from dataclasses import replace
from typing import Iterable

from .node import ExpressionNode
from .sources import TempScoreSource
from .operations import Operation, BinaryOperation, UnaryOperation


class UnaryCondition(UnaryOperation):
    def unroll(self) -> Iterable["Operation"]:
        *nodes, value = self.value.unroll()

        yield from nodes

        output = TempScoreSource.create()
        store = (output, "success")
        yield replace(self, value=value, store=(store,))
        yield output

class BinaryCondition(BinaryOperation):
    def unroll(self) -> Iterable[Operation]:
        *former_nodes, former = self.former.unroll()
        *latter_nodes, latter = self.latter.unroll()

        yield from former_nodes
        yield from latter_nodes

        output = TempScoreSource.create()
        store = (output, "success")
        yield replace(self, former=former, latter=latter, store=(store,))
        yield output


@ExpressionNode.link("branch", unary=True)
@contextmanager
def branch(node: ExpressionNode):
    yield from node.emit("_resolve_branch")


# @ExpressionNode.link("eq")
# class Equal(Operation): ...


# @ExpressionNode.link("ne")
# class NotEqual(Operation): ...


@ExpressionNode.link("not", unary=True)
class Not(UnaryCondition):
    ...

@ExpressionNode.link("lt")
class LessThan(BinaryCondition):
    ...


@ExpressionNode.link("gt")
class GreaterThan(BinaryCondition):
    ...


@ExpressionNode.link("le")
class LessThanOrEqualTo(BinaryCondition):
    ...


@ExpressionNode.link("ge")
class GreaterThanOrEqualTo(BinaryCondition):
    ...
