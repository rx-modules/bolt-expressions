from dataclasses import dataclass, field
from functools import cache
from itertools import count
from typing import Callable, ClassVar, Union

from nbtlib import Compound, Path

from . import operations as op
from .literals import convert_tag
from .node import ExpressionNode

# from rich.pretty import pprint


SOLO_COLON = slice(None, None, None)


class Source(ExpressionNode):
    ...


@dataclass(unsafe_hash=True, order=False)
class ScoreSource(Source):
    scoreholder: str
    objective: str

    @classmethod
    def on_rebind(cls, callback: Callable):
        cls._rebind = callback

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
        cls._created = callback

    @classmethod
    def create(cls, value: Union[int, float]):
        node = super().create(f"${int(value)}", cls.objective)
        cls._created(node)
        return node


class TempScoreSource(ScoreSource):
    objective: str = "temp"
    count: ClassVar[int] = -1

    @classmethod
    def create(cls):
        cls.count += 1
        return super().create(f"$i{cls.count}", cls.objective)


def parse_compound(value: Union[str, dict, Path, Compound]):
    if type(value) in (Path, Compound):
        return value
    if type(value) is dict:
        return convert_tag(value)
    return Path(value)


@dataclass(unsafe_hash=True, order=False)
class DataSource(Source):
    _type: str
    _target: str
    _path: Path = field(default_factory=Path)
    _scale: float = 1
    _number_type: str = "int"

    _constructed: bool = field(hash=False, default=False)

    def __post_init__(self):
        self._constructed = True

    @classmethod
    def on_rebind(cls, callback: Callable):
        cls._rebind = callback

    def unroll(self):
        temp_var = TempScoreSource.create()
        yield op.Set.create(temp_var, self)
        yield temp_var

    def __rebind__(self, other):
        self._rebind(self, other)
        return self

    def __setattr__(self, key: str, value):
        if not self._constructed:
            super().__setattr__(key, value)
        else:
            self.__setitem__(key, value)

    def __setitem__(self, key: str, value):
        child = self.__getitem__(key)
        child._rebind(child, value)

    def __getitem__(self, key: Union[str, int, Path, Compound]) -> "DataSource":
        if key is SOLO_COLON:
            # self[:]
            return self.all()
        if type(key) is str and key[0] == "{" and key[-1] == "}":
            # self[{abc:1b}]
            return self.filtered(key)
        # self[0] or self.foo
        path = self._path[key]
        return self._copy(path=path)

    __getattr__ = __getitem__

    def __call__(
        self,
        matching: Union[str, Path, Compound] = None,
        scale: float = None,
        type: str = None,
    ) -> "DataSource":
        """Create a new DataSource with modified properties."""
        if matching is not None:
            path = self._path[parse_compound(matching)]
        else:
            path = self._path
        return self._copy(
            path=path,
            scale=scale if scale is not None else self._scale,
            number_type=type if type is not None else self._number_type,
        )

    def __str__(self):
        return f"{self._type} {self._target} {self._path}"

    def __repr__(self):
        return f'"{str(self)}"'

    def _copy(self, **kwargs) -> "DataSource":
        """Create a new DataSource with overwritten properties."""
        return DataSource.create(
            _type=kwargs.get("type", self._type),
            _target=kwargs.get("target", self._target),
            _path=kwargs.get("path", self._path),
            _scale=kwargs.get("scale", self._scale),
            _number_type=kwargs.get("number_type", self._number_type),
        )

    def all(self) -> "DataSource":
        path = self._path + "[]"
        return self._copy(path=path)

    def filtered(self, value: Union[str, Path, Compound]):
        compound = parse_compound(value)
        path = self._path[:][compound]
        return self._copy(path=path)
