from dataclasses import dataclass, field, replace
from typing import Any, ClassVar, Union

from nbtlib import Compound, Path # type: ignore

from .optimizer import IrData, IrScore, DataTargetType
from .literals import Literal, convert_tag
from .node import ExpressionNode
from .operations import Add, Append, Divide, Enable, InPlaceMerge, Insert, Merge, Modulus, Multiply, Prepend, Remove, Reset, Set, Subtract, binary_operator

# from rich.pretty import pprint

__all__ = [
    "Source",
    "ScoreSource",
    "DataSource",
    "parse_compound",
]

SOLO_COLON = slice(None, None, None)


class Source(ExpressionNode):
    ...


def rebind(left: ExpressionNode, right: Any):
    right_node = right if isinstance(right, ExpressionNode) else Literal(value=right, ctx=left.ctx)
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
    _default_nbt_type: ClassVar[str] = "int"
    _default_floating_point_type: ClassVar[str] = "double"
    _type: DataTargetType
    _target: str
    _path: Path = field(default_factory=Path)
    _scale: float = 1
    _nbt_type: str = None

    _constructed: bool = field(hash=False, default=False, init=False)

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
            nbt_type=self._nbt_type,
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
        return replace(self, _path=path)

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

        return replace(
            self,
            _path=path,
            _scale=scale if scale is not None else self._scale,
            _nbt_type=type if type is not None else self._nbt_type,
        )

    def __str__(self):
        return f"{self._type} {self._target} {self._path}"

    def __repr__(self):
        return f'"{str(self)}"'

    def get_type(self):
        return self._nbt_type if self._nbt_type else self._default_nbt_type

    def all(self) -> "DataSource":
        path = self._path + "[]"
        return replace(self, _path=path)

    def filtered(self, value: Union[str, Path, Compound]):
        compound = parse_compound(value)
        path = self._path[:][compound]
        return replace(self, _path=path)

    def component(self, **tags):
        return {"nbt": str(self._path), self._type: self._target, **tags}
