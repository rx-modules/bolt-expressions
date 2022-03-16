from dataclasses import dataclass
from typing import Iterable, List, Union

from .node import ExpressionNode
from .sources import ConstantScoreSource, Source, TempScoreSource

GenericValue = Union["Operation", "Source", int]


@dataclass(unsafe_hash=False, order=False)
class Operation(ExpressionNode):
    former: GenericValue
    latter: GenericValue

    @classmethod
    def create(cls, former: GenericValue, latter: GenericValue):
        """Factory method to create new operations"""

        # TODO: int is hardcoded, we need to generate this stuff
        if not isinstance(former, ExpressionNode):
            former = ConstantScoreSource.create(former)
        if not isinstance(latter, ExpressionNode):
            latter = ConstantScoreSource.create(latter)

        return super().create(former, latter)

    def unroll(self) -> Iterable["Operation"]:
        *former_nodes, former_var = self.former.unroll()
        *latter_nodes, latter_var = self.latter.unroll()

        yield from former_nodes
        yield from latter_nodes

        if type(self) is not Set:
            temp_var = TempScoreSource.create()
            yield Set.create(temp_var, former_var)
            yield self.__class__.create(temp_var, latter_var)
            yield temp_var
        else:
            yield Set.create(former_var, latter_var)


# fmt: off
@ExpressionNode.link("rebind")
class Set(Operation): ...


@ExpressionNode.link("add")
@ExpressionNode.link("radd", reverse=True)
class Add(Operation):
    @classmethod
    def create(cls, former: GenericValue, latter: GenericValue):
        if not isinstance(former, Operation) and isinstance(latter, Operation):
            return super().create(latter, former)
        return super().create(former, latter)


@ExpressionNode.link("sub")
@ExpressionNode.link("rsub", reverse=True)
class Subtract(Operation): ...


@ExpressionNode.link("mul")
@ExpressionNode.link("rmul", reverse=True)
class Multiply(Operation):
    @classmethod
    def create(cls, former: GenericValue, latter: GenericValue):
        if not isinstance(former, Operation) and isinstance(latter, Operation):
            return super().create(latter, former)
        return super().create(former, latter)


@ExpressionNode.link("truediv")
@ExpressionNode.link("rtruediv", reverse=True)
class Divide(Operation): ...


@ExpressionNode.link("mod")
@ExpressionNode.link("rmod", reverse=True)
class Modulus(Operation): ...


class If(Operation): ...


@ExpressionNode.link("eq")
class Equal(Operation): ...


@ExpressionNode.link("ne")
class NotEqual(Operation): ...


@ExpressionNode.link("lt")
class LessThan(Operation): ...


@ExpressionNode.link("gt")
class GreaterThan(Operation): ...


@ExpressionNode.link("le")
class LessThanOrEqualTo(Operation): ...


@ExpressionNode.link("ge")
class GreaterThanOrEqualTo(Operation): ...
# fmt: on
