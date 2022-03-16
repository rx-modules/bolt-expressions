from dataclasses import dataclass
from typing import Iterable, List, Union

from functools import cache
from itertools import count

GenericValue = Union["Operation", "Source", int]


@dataclass(frozen=True)
class ExpressionNode:
    def __add__(self, other: "ExpressionNode"):
        return Add.create(self, other)

    def __radd__(self, other: "ExpressionNode"):
        return Add.create(other, self)

    def __sub__(self, other: "ExpressionNode"):
        return Subtract.create(self, other)

    def __rsub__(self, other: "ExpressionNode"):
        return Subtract.create(other, self)

    def __mul__(self, other: "ExpressionNode"):
        return Multiply.create(self, other)

    def __rmul__(self, other: "ExpressionNode"):
        return Multiply.create(other, self)

    def __truediv__(self, other: "ExpressionNode"):
        return Divide.create(self, other)

    def __rtruediv__(self, other: "ExpressionNode"):
        return Divide.create(other, self)

    def __floordiv__(self, other: "ExpressionNode"):
        return Divide.create(self, other)

    def __rfloordiv__(self, other: "ExpressionNode"):
        return Divide.create(other, self)

    def __mod__(self, other: "ExpressionNode"):
        return Modulus.create(self, other)

    def __rmod__(self, other: "ExpressionNode"):
        return Modulus.create(other, self)

    # def set(self, other: "ExpressionNode"):
    #     ...

    # def get(self):
    #     ...

    @classmethod
    def create(cls, *args, **kwargs):
        return cls(*args, **kwargs)

    def unroll(self) -> Iterable["Operation"]:
        yield self


@dataclass(frozen=True)
class Source(ExpressionNode):
    ...


@dataclass(frozen=True)
class ScoreSource(Source):
    scoreholder: str
    objective: str

    def __str__(self):
        return f"{self.scoreholder} {self.objective}"

    def __repr__(self):
        return f'"{str(self)}"'


class ConstantScoreSource(ScoreSource):
    @classmethod
    def create(cls, value: Union[int, float]):
        return super().create(f"${int(value)}", "constant")


class TempScoreSource(ScoreSource):
    @classmethod
    @property
    @cache
    def infinite(cls):
        yield from count()

    @classmethod
    def create(cls):
        return super().create(f"$i{next(cls.infinite)}", "temp")


@dataclass(frozen=True)
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

        current_var = TempScoreSource.create()

        yield from former_nodes
        yield from latter_nodes

        if type(self) is not Set:
            yield Set.create(current_var, former_var)
            yield self.__class__.create(current_var, latter_var)
            yield current_var
        else:
            yield Set.create(former_var, latter_var)


class Set(Operation):
    ...


class Add(Operation):
    @classmethod
    def create(cls, former: GenericValue, latter: GenericValue):
        if (
            not isinstance(former, Operation)
            and isinstance(latter, Operation)
        ): return super().create(latter, former)
        return super().create(former, latter)


class Subtract(Operation):
    ...


class Multiply(Operation):
    @classmethod
    def create(cls, former: GenericValue, latter: GenericValue):
        if (
            not isinstance(former, Operation)
            and isinstance(latter, Operation)
        ): return super().create(latter, former)
        return super().create(former, latter)



class Divide(Operation):
    ...


class Modulus(Operation):
    ...
