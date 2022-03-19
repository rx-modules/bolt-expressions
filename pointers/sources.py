from dataclasses import dataclass
from functools import cache
from itertools import count
from typing import Callable, Union

from .node import ExpressionNode


class Source(ExpressionNode): ...


@dataclass(unsafe_hash=True, order=False)
class ScoreSource(Source):
    scoreholder: str
    objective: str

    @classmethod
    def on_rebind(cls, callback: Callable):
        setattr(cls, '_rebind', callback)
    
    def __rebind__(self, other: ExpressionNode):
        self._rebind(self, other)
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
