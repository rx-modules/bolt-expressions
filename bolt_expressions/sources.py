from dataclasses import dataclass
from functools import cache
from itertools import count
from typing import Callable, Union

from .node import ExpressionNode


# fmt: off
class Source(ExpressionNode): ...
# fmt: on

@dataclass(unsafe_hash=True, order=False)
class ScoreSource(Source):
    scoreholder: str
    objective: str

    @classmethod
    def on_rebind(cls, callback: Callable):
        setattr(cls, "_rebind", callback)

    def __rebind__(self, other: ExpressionNode):
        self._rebind(self, other)
        return self

    def __str__(self):
        return f"{self.scoreholder} {self.objective}"

    def __repr__(self):
        return f'"{str(self)}"'


class ConstantScoreSource(ScoreSource):
    objective: str = "const"

    @classmethod
    def on_created(cls, callback: Callable):
        setattr(cls, "_created", callback)

    @classmethod
    def create(cls, value: Union[int, float]):
        node = super().create(f"${int(value)}", cls.objective)
        cls._created(node)
        return node


class TempScoreSource(ScoreSource):
    objective: str = "temp"

    @classmethod
    @property
    @cache
    def infinite(cls):
        yield from count()

    @classmethod
    def create(cls):
        return super().create(f"$i{next(cls.infinite)}", cls.objective)


@dataclass(unsafe_hash=False, order=False)
class DataSource(Source):
    target: str
    path: str  # TODO: pointers >_<
