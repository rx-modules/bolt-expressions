from abc import ABC, abstractmethod
from dataclasses import dataclass, field, replace
from typing import Any, Union, cast

from nbtlib import Compound, Path

from .optimizer import IrData, IrScore, DataTargetType
from .literals import Literal
from .node import ExpressionNode
from .operations import (
    Add,
    Append,
    Divide,
    Enable,
    InPlaceMerge,
    Insert,
    Merge,
    Modulus,
    Multiply,
    Prepend,
    Remove,
    Reset,
    Set,
    Subtract,
    binary_operator,
)
from .typing import NbtType, Accessor, access_type, access_type_by_path, convert_type, convert_tag, is_type, literal_types


__all__ = [
    "Source",
    "ScoreSource",
    "DataSource",
    "parse_compound",
]

SOLO_COLON = slice(None, None, None)


class Source(ExpressionNode, ABC):
    @abstractmethod
    def component(self) -> Any:
        ...


def rebind(left: ExpressionNode, right: Any):
    right_node = (
        right
        if isinstance(right, ExpressionNode)
        else Literal(value=right, ctx=left.ctx)
    )
    op = Set(former=left, latter=right_node, ctx=left.ctx)
    left.expr.resolve(op)

    return left


@dataclass(unsafe_hash=True, order=False)
class ScoreSource(Source):
    scoreholder: str
    objective: str

    __rebind__ = rebind
    __add__, __radd__ = binary_operator(Add, reverse=True)
    __sub__, __rsub__ = binary_operator(Subtract, reverse=True)
    __mul__, __rmul__ = binary_operator(Multiply, reverse=True)
    __truediv__, __rtruediv__ = binary_operator(Divide, reverse=True)
    __mod__, __rmod__ = binary_operator(Modulus, reverse=True)

    def enable(self):
        self.expr.resolve(Enable(target=self, ctx=self.ctx))

    def reset(self):
        self.expr.resolve(Reset(target=self, ctx=self.ctx))

    def __str__(self):
        return f"{self.scoreholder} {self.objective}"

    def __repr__(self):
        return f'"{str(self)}"'

    def component(self, **tags: Any):
        return {
            "score": {"name": self.scoreholder, "objective": self.objective},
            **tags,
        }

    def unroll(self):
        return (), IrScore(holder=self.scoreholder, obj=self.objective)

    @property
    def holder(self):
        return self.scoreholder

    @property
    def obj(self):
        return self.objective


def parse_compound(value: Union[str, dict, Path, Compound]):
    if isinstance(value, (Path, Compound)):
        return value
    if isinstance(value, dict):
        return convert_tag(value)
    return Path(value)


@dataclass(unsafe_hash=True, order=False)
class DataSource(Source):
    _type: DataTargetType
    _target: str
    _path: Path = field(default_factory=Path)
    _scale: float = 1
    writetype: NbtType = Any

    _constructed: bool = field(hash=False, default=False, init=False)

    @property
    def readtype(self) -> NbtType:
        return self.writetype

    __rebind__ = rebind
    __add__, __radd__ = binary_operator(Add, reverse=True)
    __sub__, __rsub__ = binary_operator(Subtract, reverse=True)
    __mul__, __rmul__ = binary_operator(Multiply, reverse=True)
    __truediv__, __rtruediv__ = binary_operator(Divide, reverse=True)
    __mod__, __rmod__ = binary_operator(Modulus, reverse=True)
    __or__, __ror__ = binary_operator(Merge, reverse=True)

    def insert(self, index: int, value: Any) -> None:
        self.expr.resolve(Insert(former=self, latter=value, index=index, ctx=self.ctx))

    def append(self, value: Any) -> None:
        self.expr.resolve(Append(former=self, latter=value, ctx=self.ctx))

    def prepend(self, value: Any) -> None:
        self.expr.resolve(Prepend(former=self, latter=value, ctx=self.ctx))

    def merge(self, value: Any) -> None:
        self.expr.resolve(InPlaceMerge(former=self, latter=value, ctx=self.ctx))

    def remove(self, sub_path: Any = None) -> None:
        target = self if sub_path is None else self[sub_path]
        self.expr.resolve(Remove(target=target, ctx=self.ctx))

    def __post_init__(self):
        super().__post_init__()

        self._constructed = True

    def unroll(self):
        node = IrData(
            type=self._type,
            target=self._target,
            path=self._path,
            nbt_type=self.writetype,
            scale=self._scale,
        )
        return (), node

    def __setattr__(self, key: str, value):
        if not self._constructed:
            super().__setattr__(key, value)
        else:
            self.__setitem__(key, value)

    def __setitem__(self, key: str, value):
        child = self.__getitem__(key)
        child.__rebind__(value)

    def __getitem__(
        self, key: Union[slice, str, dict[str, Any], int, NbtType, Path]
    ) -> "DataSource":
        if key is SOLO_COLON:
            # self[:]
            return self.all()

        if is_type(key):
            return replace(self, writetype=convert_type(key))

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
        return replace(self, _path=path, writetype=writetype)

    __getattr__ = __getitem__

    def _get_property_type(self, nbt_type: NbtType, child_path: Path) -> NbtType:
        path = cast(tuple[Accessor, ...], tuple(child_path))
        length = len(self._path)
        relative_path = path[length:]

        return access_type_by_path(nbt_type, relative_path, self.expr.ctx) or Any

    def __call__(
        self,
        matching: str | Path | Compound | None = None,
        scale: float | None = None,
        type: str | None = None,
    ) -> "DataSource":
        """Create a new DataSource with modified properties."""
        if matching is not None:
            path = self._path[parse_compound(matching)]
        else:
            path = self._path

        writetype = literal_types[type] if type else self.writetype

        return replace(
            self,
            _path=path,
            _scale=scale if scale is not None else self._scale,
            writetype=writetype,
        )

    def __str__(self):
        return f"{self._type} {self._target} {self._path}"

    def __repr__(self):
        return f'"{str(self)}"'

    def all(self) -> "DataSource":
        path = self._path + "[]"
        return replace(self, _path=path)

    def filtered(self, value: Union[str, Path, Compound]):
        compound = parse_compound(value)
        path = self._path[:][compound]
        return replace(self, _path=path)

    def component(self, **tags):
        return {"nbt": str(self._path), self._type: self._target, **tags}
