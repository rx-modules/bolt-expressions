from dataclasses import dataclass
from functools import cache
from itertools import count
from typing import Union

from .node import ExpressionNode
from . import operations as op


class Source(ExpressionNode): ...


@dataclass(unsafe_hash=True, order=False)
class ScoreSource(Source):
    scoreholder: str
    objective: str

    def __rebind__(self, other: ExpressionNode):
        op.Set.create(self, other).resolve()
        return self

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


@dataclass(unsafe_hash=False, order=False)
class DataSource(Source):
    target: str
    path: str  # TODO: pointers >_<
