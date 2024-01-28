from abc import ABC, abstractmethod
from dataclasses import dataclass, field, replace
from typing import Any, ClassVar, ParamSpec, Protocol, TypedDict, Union, cast, is_typeddict, overload
from beet import Context
from bolt.utils import internal

from nbtlib import Compound, Path, ListIndex, CompoundMatch, NamedKey

from .node import Expression
from .typing import NbtType, is_compound_type
from .utils import type_name

from .optimizer import IrData, IrScore, DataTargetType
from .literals import Literal
from .node import Expression, ExpressionNode
from .operations import (
    Add,
    Append,
    Cast,
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
from .typing import NbtType, Accessor, access_type, convert_type, convert_tag, is_array_type, is_compound_alias, is_list_type, is_numeric_type, is_string_type, is_type, literal_types


__all__ = [
    "Source",
    "ScoreSource",
    "DataSourceSubclassDict",
    "DataSource",
    "GenericDataSource",
    "StringDataSource",
    "NumericDataSource",
    "SequenceDataSource",
    "CompoundDataSource",
    "parse_compound",
]

SOLO_COLON = slice(None, None, None)


class Source(ExpressionNode, ABC):
    @abstractmethod
    def component(self) -> Any:
        ...


@internal
def rebind(left: ExpressionNode, right: Any, cast: NbtType | None = None):
    right_node = (
        right
        if isinstance(right, ExpressionNode)
        else Literal(value=right, ctx=left.ctx)
    )
    if cast is None:
        op = Set(former=left, latter=right_node, ctx=left.ctx)
    else:
        op = Cast(former=left, latter=right_node, cast_type=cast, ctx=left.ctx)
    
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


class DataSourceSubclassDict(TypedDict):
    numeric: type["DataSource"]
    string: type["DataSource"]
    array: type["DataSource"]
    list: type["DataSource"]
    compound: type["DataSource"]
    generic: type["DataSource"]


@dataclass(unsafe_hash=True, order=False)
class DataSource(Source, ABC):
    _type: DataTargetType
    _target: str
    _path: Path = field(default_factory=Path)
    _scale: float = 1
    writetype: NbtType = Any

    _named_key: ClassVar[bool] = False
    _list_index: ClassVar[bool] = False
    _compound_match: ClassVar[bool] = False

    _constructed: bool = field(hash=False, default=False, init=False)

    @classmethod
    def get_subclasses(cls) -> DataSourceSubclassDict:
        return {
            "numeric": NumericDataSource,
            "string": StringDataSource,
            "array": SequenceDataSource,
            "list": SequenceDataSource,
            "compound": CompoundDataSource,
            "generic": GenericDataSource,
        }

    @classmethod
    def create(
        cls,
        target_type: DataTargetType,
        target: str,
        path: Path = Path(),
        scale: float = 1,
        nbt_type: Any = Any,
        *,
        ctx: Context | Expression,
        **kwargs: Any,
    ) -> "DataSource":
        writetype = convert_type(nbt_type)
        if writetype is None:
            writetype = Any
        
        subclasses = cls.get_subclasses()

        if is_numeric_type(writetype):
            subclass = subclasses["numeric"]
        elif is_string_type(writetype):
            subclass = subclasses["string"]
        elif is_array_type(writetype):
            subclass = subclasses["array"]
        elif is_list_type(writetype):
            subclass = subclasses["list"]
        elif is_compound_type(writetype):
            subclass = subclasses["compound"]
        else:
            subclass = subclasses["generic"]

        return subclass(
            _type=target_type,
            _target=target,
            _path=path,
            _scale=scale,
            writetype=writetype,
            ctx=ctx,
            **kwargs
        )

    def __post_init__(self):
        super().__post_init__()

        self._constructed = True

    @property
    def readtype(self) -> NbtType:
        return self.writetype

    def unroll(self):
        node = IrData(
            type=self._type,
            target=self._target,
            path=self._path,
            nbt_type=self.readtype,
            scale=self._scale,
        )
        return (), node
    
    @internal
    def __rebind__(self, right: Any):
        return rebind(self, right, self.writetype)

    @internal
    def __setattr__(self, key: str, value):
        if not self._constructed:
            super().__setattr__(key, value)
        else:
            self.__setitem__(key, value)

    @internal
    def __setitem__(self, key: str, value):
        child = self.__getitem__(key)
        child.__rebind__(value)

    def __getitem__(
        self, key: Union[slice, str, dict[str, Any], int, NbtType, Path]
    ) -> Any:
        if is_type(key, allow_dict=False):
            return self.create(
                self._type, self._target, self._path, self._scale, key, ctx=self.ctx
            )

        if key is SOLO_COLON:
            sub_path = Path()[:]
        elif (
            isinstance(key, dict)
            or isinstance(key, str)
            and (key[0], key[-1]) == ("{", "}")
        ):
            compound = parse_compound(key)
            sub_path = Path()[:][compound]
        else:
            sub_path = Path()[key]

        return self._access(sub_path)

    __getattr__ = __getitem__

    def _access(self, sub_path: Path) -> "DataSource":
        if not len(sub_path):
            return self
        
        accessor, *rest = cast(tuple[Accessor, ...], tuple(sub_path))

        if isinstance(accessor, ListIndex) and not self._list_index:
            raise TypeError(f"'{type_name(self)}' object is not indexable")

        if isinstance(accessor, CompoundMatch) and not self._compound_match:
            raise TypeError(f"'{type_name(self)}' object does not support compound matching")

        if isinstance(accessor, NamedKey) and not self._named_key:
            raise TypeError(f"'{type_name(self)}' object does not have named keys")
        
        writetype = access_type(self.writetype, accessor, self.expr.ctx) or Any
        path = Path.from_accessors((*self._path, accessor)) # type: ignore

        source = self.create(self._type, self._target, path, self._scale, writetype, ctx=self.ctx)

        if not len(rest):
            return source
        
        rest_path = Path.from_accessors(tuple(rest)) # type: ignore
        return source._access(rest_path)
        

    @overload
    def __call__(self, matching: str | Path | Compound, /) -> Any:
        ...

    @overload
    def __call__(
        self,
        matching: None,
        /,
        *,
        scale: float | None = None,
        type: str | None = None,
    ) -> Any:
        ...

    def __call__(
        self,
        matching: str | Path | Compound | None = None,
        /,
        *,
        scale: float | None = None,
        type: str | None = None,
    ) -> Any:
        """Create a new DataSource with modified properties."""

        if matching is not None:
            sub_path = Path()[parse_compound(matching)]
            return self._access(sub_path)

        writetype = literal_types[type] if type else self.writetype

        return self.create(
            self._type,
            self._target,
            self._path,
            scale if scale is not None else self._scale,
            writetype,
            ctx=self.ctx
        )

    def __str__(self):
        return f"{self._type} {self._target} {self._path}"

    def __repr__(self):
        return f'"{str(self)}"'

    def component(self, **tags):
        return {"nbt": str(self._path), self._type: self._target, **tags}



class GenericDataSource(DataSource):
    _list_index: ClassVar[bool] = True
    _named_key: ClassVar[bool] = True
    _compound_match: ClassVar[bool] = True

    __add__, __radd__ = binary_operator(Add, reverse=True)
    __sub__, __rsub__ = binary_operator(Subtract, reverse=True)
    __mul__, __rmul__ = binary_operator(Multiply, reverse=True)
    __truediv__, __rtruediv__ = binary_operator(Divide, reverse=True)
    __mod__, __rmod__ = binary_operator(Modulus, reverse=True)
    __or__, __ror__ = binary_operator(Merge, reverse=True)

    @internal
    def insert(self, index: int, value: Any) -> None:
        self.expr.resolve(Insert(former=self, latter=value, index=index, ctx=self.ctx))

    @internal
    def append(self, value: Any) -> None:
        self.expr.resolve(Append(former=self, latter=value, ctx=self.ctx))

    @internal
    def prepend(self, value: Any) -> None:
        self.expr.resolve(Prepend(former=self, latter=value, ctx=self.ctx))

    @internal
    def remove(self, sub_path: Any = None) -> None:
        target = self if sub_path is None else self[sub_path]
        self.expr.resolve(Remove(target=target, ctx=self.ctx))

    @internal
    def merge(self, value: Any) -> None:
        self.expr.resolve(InPlaceMerge(former=self, latter=value, ctx=self.ctx))

class NumericDataSource(DataSource):
    __add__, __radd__ = binary_operator(Add, reverse=True)
    __sub__, __rsub__ = binary_operator(Subtract, reverse=True)
    __mul__, __rmul__ = binary_operator(Multiply, reverse=True)
    __truediv__, __rtruediv__ = binary_operator(Divide, reverse=True)
    __mod__, __rmod__ = binary_operator(Modulus, reverse=True)

class StringDataSource(DataSource):
    ...

class SequenceDataSource(DataSource):
    _list_index: ClassVar[bool] = True

    @internal
    def insert(self, index: int, value: Any) -> None:
        self.expr.resolve(Insert(former=self, latter=value, index=index, ctx=self.ctx))

    @internal
    def append(self, value: Any) -> None:
        self.expr.resolve(Append(former=self, latter=value, ctx=self.ctx))

    @internal
    def prepend(self, value: Any) -> None:
        self.expr.resolve(Prepend(former=self, latter=value, ctx=self.ctx))

    @internal
    def remove(self, sub_path: Any = None) -> None:
        target = self if sub_path is None else self[sub_path]
        self.expr.resolve(Remove(target=target, ctx=self.ctx))

class CompoundDataSource(DataSource):
    _named_key: ClassVar[bool] = True
    _compound_match: ClassVar[bool] = True

    __or__, __ror__ = binary_operator(Merge, reverse=True)

    @internal
    def merge(self, value: Any) -> None:
        self.expr.resolve(InPlaceMerge(former=self, latter=value, ctx=self.ctx))
