from contextlib import contextmanager
from typing import Iterable

from .node import ExpressionNode
from .sources import TempScoreSource
from .operations import Operation


class Condition(Operation):
    def unroll(self) -> Iterable[Operation]:
        *former_nodes, former_var = self.former.unroll()
        *latter_nodes, latter_var = self.latter.unroll()

        yield from former_nodes
        yield from latter_nodes

        temp_var = TempScoreSource.create()
        store = (temp_var, "success")
        yield self.__class__.create(former_var, latter_var, store=(store,))
        yield temp_var


@ExpressionNode.link("branch", unary=True)
@contextmanager
def branch(node: ExpressionNode):
    yield from node.emit("_resolve_branch")


# @ExpressionNode.link("eq")
# class Equal(Operation): ...


# @ExpressionNode.link("ne")
# class NotEqual(Operation): ...


@ExpressionNode.link("lt")
class LessThan(Condition):
    ...


@ExpressionNode.link("gt")
class GreaterThan(Condition):
    ...


@ExpressionNode.link("le")
class LessThanOrEqualTo(Condition):
    ...


@ExpressionNode.link("ge")
class GreaterThanOrEqualTo(Condition):
    ...
