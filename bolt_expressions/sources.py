from dataclasses import dataclass, field, replace
from functools import cache
from itertools import count
from typing import Any, Callable, ClassVar, Union, cast

from nbtlib import Compound, Double, Path

from . import operations as op
from .literals import convert_tag
from .node import ExpressionNode
from .typing import Accessor, DataType, convert_type, get_property_type_by_path, is_type

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
    if isinstance(value, (Path, Compound)):
        return value
    if isinstance(value, dict):
        return convert_tag(value)
    return Path(value)


@dataclass(unsafe_hash=True, order=False)
class DataSource(Source):
    _type: str
    _target: str
    _path: Path = field(default_factory=Path)
    _scale: float = 1

    writetype: DataType = Any

    _constructed: bool = field(hash=False, default=False, init=False)

    _default_floating_point_type: ClassVar[type] = Double

    @property
    def readtype(self) -> DataType:
        return self.writetype

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

    def __getitem__(
        self, key: Union[slice, str, dict[str, Any], int, DataType, Path]
    ) -> "DataSource":
        if is_type(key):
            key = cast(DataType, key)
            return self._cast(key)

        if key is SOLO_COLON:
            path = self._path + "[]"
        elif (
            isinstance(key, dict)
            or isinstance(key, str)
            and (key[0], key[-1]) == ("{", "}")
        ):
            compound = parse_compound(key)
            path = self._path[:][compound]
        else:
            path = self._path[key]

        writetype = self._get_property_type(self.writetype, path)

        # TODO: validate by readtype

        return replace(self, _path=path, writetype=writetype)

    __getattr__ = __getitem__

    def __call__(
        self,
        matching: Union[str, Path, Compound] = None,
        scale: float = None,
        type: DataType | str = None,
    ) -> "DataSource":
        """Create a new DataSource with modified properties."""
        if matching is not None:
            path = self._path[parse_compound(matching)]
            type = self._get_property_type(self.writetype, path)
        else:
            path = self._path

        return replace(
            self,
            _path=path,
            _scale=scale if scale is not None else self._scale,
            writetype=type if type is not None else self.writetype,
        )

    def _cast(self, type: DataType) -> "DataSource":
        type = convert_type(type)

        return replace(self, writetype=type)

    def _get_property_type(self, data_type: DataType, child_path: Path):
        relative = cast(tuple[Accessor, ...], tuple(child_path)[len(self._path) :])

        return get_property_type_by_path(data_type, relative)

    def __str__(self):
        return f"{self._type} {self._target} {self._path}"

    def __repr__(self):
        return f'"{str(self)}"'

    def component(self, **tags):
        return {"nbt": str(self._path), self._type: self._target, **tags}
