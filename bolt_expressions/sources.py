from dataclasses import dataclass, field
from functools import cache
from itertools import count
from typing import Callable, ClassVar, Union

from nbtlib import Compound, Path

from . import operations as op
from .literals import convert_tag
from .node import ExpressionNode

# from rich.pretty import pprint

__all__ = [
    "Source",
    "ScoreSource",
    "ConstantScoreSource",
    "TempScoreSource",
    "DataSource",
    "parse_compound",
]

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

    def component(self, **tags):
        return {
            "score": {"name": self.scoreholder, "objective": self.objective},
            **tags,
        }

    @property
    def holder(self):
        return self.scoreholder

    @property
    def obj(self):
        return self.objective


@dataclass(unsafe_hash=True, order=False)
class ConstantScoreSource(ScoreSource):
    objective: str = "const"
    value: int = field(hash=False, kw_only=True)

    @classmethod
    def create(cls, value: int):
        return super().create(f"${value}", cls.objective, value=value)


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
    _default_nbt_type: ClassVar[str] = "int"
    _default_floating_point_type: ClassVar[str] = "double"
    _type: str
    _target: str
    _path: Path = field(default_factory=Path)
    _scale: float = 1
    _nbt_type: str = None

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
        if (
            isinstance(key, dict)
            or isinstance(key, str)
            and (key[0], key[-1]) == ("{", "}")
        ):
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
            nbt_type=type if type is not None else self._nbt_type,
        )

    def __str__(self):
        return f"{self._type} {self._target} {self._path}"

    def __repr__(self):
        return f'"{str(self)}"'

    def _copy(self, **kwargs) -> "DataSource":
        """Create a new DataSource with overwritten properties."""
        return self.__class__.create(
            _type=kwargs.get("type", self._type),
            _target=kwargs.get("target", self._target),
            _path=kwargs.get("path", self._path),
            _scale=kwargs.get("scale", self._scale),
            _nbt_type=kwargs.get("nbt_type", self._nbt_type),
        )

    def get_type(self):
        return self._nbt_type if self._nbt_type else self._default_nbt_type

    def all(self) -> "DataSource":
        path = self._path + "[]"
        return self._copy(path=path)

    def filtered(self, value: Union[str, Path, Compound]):
        compound = parse_compound(value)
        path = self._path[:][compound]
        return self._copy(path=path)

    def component(self, **tags):
        return {"nbt": str(self._path), self._type: self._target, **tags}
