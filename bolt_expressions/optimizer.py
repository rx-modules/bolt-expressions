from abc import ABC
from bisect import bisect_left
from contextlib import contextmanager
from dataclasses import dataclass, field, replace
from enum import Enum
from fractions import Fraction
from types import TracebackType
from typing import (
    Any,
    Callable,
    Generator,
    Generic,
    Iterable,
    Iterator,
    Literal,
    NamedTuple,
    TypeGuard,
    TypeVar,
    Union,
    Concatenate,
    ParamSpec,
    cast,
)
from beet import Context
from mecha import AbstractChildren, AbstractNode, AstNode
from bolt.utils import internal

from nbtlib import (  # type:ignore
    Int,
    Double,
    Float,
    Numeric,
    String,
    Compound,
    Path,
    NamedKey,
    CompoundMatch,
    List,
    ListIndex,
)

from .typing import (
    Accessor,
    NbtType,
    NbtValue,
    access_type_by_path,
    convert_tag,
    infer_type,
    is_array_type,
    is_compound_type,
    is_list_type,
    is_numeric_type,
    is_string_type,
    literal_types,
    unwrap_optional_type,
)
from rich.pretty import pprint

__all__ = [
    "Rule",
    "SmartRule",
    "SmartGenerator",
    "Optimizer",
    "use_smart_generator",
    "smart_generator",
    "noncommutative_set_collapsing",
    "commutative_set_collapsing",
    "data_set_scaling",
    "data_get_scaling",
    "multiply_divide_by_fraction",
    "multiply_divide_by_one_removal",
    "add_subtract_by_zero_removal",
    "set_to_self_removal",
    "set_and_get_cleanup",
    "literal_to_constant_replacement",
    "DataTargetType",
    "IrNode",
    "IrSource",
    "IrScore",
    "IrLiteral",
    "IrOperation",
    "IrUnary",
    "IrBinary",
    "is_op",
    "is_unary",
    "is_binary",
]

T = TypeVar("T")


class IrNode(AbstractNode):
    ...


IrNodeType = TypeVar("IrNodeType", bound=IrNode, covariant=True)
AstNodeType = TypeVar("AstNodeType", bound=AstNode, covariant=True)


@dataclass(frozen=True, kw_only=True)
class IrRaw(IrNode, Generic[AstNodeType]):
    node: AstNodeType


class IrChildren(AbstractChildren[IrNodeType]):
    @classmethod
    def from_ast(
        cls, children: Iterable[AstNodeType]
    ) -> "IrChildren[IrRaw[AstNodeType]]":
        return IrChildren(IrRaw(node=node) for node in children)


class IrSource(IrNode, ABC):
    def to_tuple(self) -> "SourceTuple":
        ...


@dataclass(frozen=True, kw_only=True)
class IrScore(IrSource):
    holder: str
    obj: str

    def to_tuple(self) -> "ScoreTuple":
        return ScoreTuple(self.holder, self.obj)


class IrBoolScore(IrScore):
    ...


DataTargetType = Literal["storage", "entity", "block"]


@dataclass(frozen=True, kw_only=True)
class IrData(IrSource):
    type: DataTargetType
    target: str
    path: Path
    nbt_type: NbtType = Any
    scale: float | None = None

    def to_tuple(self) -> "DataTuple":
        return DataTuple(self.type, self.target, self.path)


@dataclass(frozen=True, kw_only=True)
class IrDataString(IrData):
    range: int | tuple[int | None, int | None]

    @property
    def normalized_range(self) -> tuple[int, int | None]:
        if isinstance(self.range, tuple):
            start, end = self.range
        else:
            start = self.range
            end = None if start == -1 else self.range + 1

        if start is None:
            start = 0

        return (start, end)

    def to_tuple(self) -> "StringDataTuple":  # type: ignore
        return StringDataTuple(self.type, self.target, self.path, self.normalized_range)


@dataclass(frozen=True, kw_only=True)
class IrLiteral(IrNode):
    value: NbtValue


CompositeNbtValue = Union[
    NbtValue,
    list[Union["CompositeNbtValue", IrSource]],
    dict[str, Union["CompositeNbtValue", IrSource]],
]


@dataclass(frozen=True, kw_only=True)
class IrCompositeLiteral(IrNode):
    value: CompositeNbtValue


@dataclass(frozen=True, kw_only=True)
class IrCondition(IrNode):
    op: str
    negated: bool = False


@dataclass(frozen=True, kw_only=True)
class IrUnaryCondition(IrCondition):
    target: IrSource


@dataclass(frozen=True, kw_only=True)
class IrBinaryCondition(IrCondition):
    left: IrSource | IrLiteral
    right: IrSource | IrLiteral


def is_condition(
    obj: Any, op: str | Iterable[str] | None = None
) -> TypeGuard[IrCondition]:
    if not isinstance(obj, IrCondition):
        return False

    if op is None:
        return True

    if isinstance(op, str):
        op = (op,)

    return obj.op in op


def is_unary_condition(
    obj: Any, op: str | Iterable[str] | None = None
) -> TypeGuard[IrUnaryCondition]:
    return is_condition(obj, op) and isinstance(obj, IrUnaryCondition)


def is_binary_condition(
    obj: Any, op: str | Iterable[str] | None = None
) -> TypeGuard[IrBinaryCondition]:
    return is_condition(obj, op) and isinstance(obj, IrBinaryCondition)


class StoreType(Enum):
    result = "result"
    success = "success"


@dataclass(frozen=True, kw_only=True)
class IrStore(IrNode):
    type: StoreType
    value: IrSource
    scale: float = 1
    cast_type: NbtType = Any


OperandType = IrLiteral | IrSource | IrCondition


@dataclass(frozen=True, kw_only=True)
class IrOperation(IrNode):
    op: str
    store: IrChildren[IrStore] = field(default_factory=IrChildren)

    destructive: bool = True

    @property
    def targets(self) -> tuple[IrSource, ...]:
        return tuple(s.value for s in self.store)

    @property
    def operands(self) -> tuple[IrSource | IrCondition | IrLiteral, ...]:
        return ()


@dataclass(frozen=True, kw_only=True)
class IrUnary(IrOperation):
    target: IrSource | IrCondition

    @property
    def targets(self):
        targets = super().targets

        if self.destructive and isinstance(self.target, IrSource):
            return targets + (self.target,)

        return targets

    @property
    def operands(self) -> tuple[IrSource | IrCondition]:
        return (self.target,)


@dataclass(frozen=True, kw_only=True)
class IrBinary(IrOperation):
    left: IrSource
    right: IrSource | IrCondition | IrLiteral

    uses_left: bool = True

    @property
    def targets(self):
        targets = super().targets

        if self.destructive:
            return targets + (self.left,)

        return targets

    @property
    def operands(self) -> tuple[IrSource | IrCondition | IrLiteral, ...]:
        if not self.uses_left:
            return (self.right,)

        return (self.left, self.right)


@dataclass(frozen=True, kw_only=True)
class IrGetLength(IrUnary):
    op: str = field(default="get_length", init=False)
    destructive: bool = field(default=False, init=False)


@dataclass(frozen=True, kw_only=True)
class IrInsert(IrBinary):
    op: str = field(default="insert", init=False)
    destructive: bool = field(default=True, init=False)
    index: int


@dataclass(frozen=True, kw_only=True)
class IrSet(IrBinary):
    op: str = field(default="set", init=False)
    destructive: bool = field(default=True, init=False)
    uses_left: bool = field(default=False, init=False)


@dataclass(frozen=True, kw_only=True)
class IrCast(IrBinary):
    op: str = field(default="cast", init=False)
    destructive: bool = field(default=True, init=False)
    uses_left: bool = field(default=False, init=False)
    cast_type: NbtType = Any
    scale: float = 1


@dataclass(frozen=True, kw_only=True)
class IrBranch(IrUnary):
    op: str = field(default="branch", init=False)
    destructive: bool = field(default=False, init=False)

    children: IrChildren[Any]


def is_op(obj: Any, op: str | Iterable[str] | None = None) -> TypeGuard[IrOperation]:
    if not isinstance(obj, IrOperation):
        return False

    if op is None:
        return True

    if isinstance(op, str):
        op = (op,)

    return obj.op in op


def is_unary(obj: Any, op: str | Iterable[str] | None = None) -> TypeGuard[IrUnary]:
    return is_op(obj, op) and isinstance(obj, IrUnary)


def is_binary(obj: Any, op: str | Iterable[str] | None = None) -> TypeGuard[IrBinary]:
    return is_op(obj, op) and isinstance(obj, IrBinary)


def is_copy_op(node: Any) -> TypeGuard[IrBinary]:
    if is_binary(node, "set"):
        return True

    if isinstance(node, IrCast):
        cast_type = unwrap_optional_type(node.cast_type)

        if node.scale != 1:
            return False

        if isinstance(node.left, IrScore) and isinstance(node.right, IrScore):
            return True

        if isinstance(node.left, IrData) and isinstance(node.right, IrData):
            if cast_type == unwrap_optional_type(node.right.nbt_type):
                return True
            if cast_type is Any:
                return True

        if isinstance(node.right, IrLiteral) and cast_type is Any:
            return True

        return False

    return False


SCORE_OPERATIONS = ("set", "add", "sub", "mul", "div", "mod", "min", "max")

DATA_OPERATIONS = ("set", "remove", "insert", "append", "prepend", "merge")


class SmartGenerator(Generator[T, None, None]):
    """Implements `.push(val)` which allows you to 'prepend' values to a generator.
    Allows you to peek values in the future, and return them to be consumed later.

    >>> gen = SmartGenerator(i for i in range(10))
    >>> val = next(gen)
    >>> gen.push(val)
    >>> next(gen)
    0
    """

    _values: Iterator[T]
    _pre: list[T]

    def __init__(self, values: Iterable[T]):
        self._values = iter(values)
        self._pre = []

    def __iter__(self):
        return self

    def __next__(self) -> T:
        if self._pre:
            return self._pre.pop()

        return next(self._values)

    def push(self, val: T | None):
        if val is not None:
            self._pre.append(val)

    def send(self, __value: None) -> T:
        ...

    def throw(
        self,
        __typ: BaseException | type[BaseException],
        __val: BaseException | object = None,
        __tb: TracebackType | None = None,
    ) -> T:
        ...


P = ParamSpec("P")
Rule = Callable[Concatenate[Iterable[T], P], Iterable[T]]

SmartRule = Callable[Concatenate[SmartGenerator[T], P], Iterable[T]]


def use_smart_generator(func: SmartRule[T, P]) -> Rule[T, P]:
    """
    Provides a `SmartGenerator` object as first argument to the decorated rule.
    Returned function still takes an `Iterable` object.
    """

    def rule(arg: Iterable[T], *args: P.args, **kwargs: P.kwargs) -> Iterable[T]:
        return func(SmartGenerator(arg), *args, **kwargs)

    return rule


def smart_generator(func: Rule[T, P]) -> Callable[[Iterable[T]], SmartGenerator[T]]:
    def rule(arg: Iterable[T], *args: P.args, **kwargs: P.kwargs):
        return SmartGenerator(func(arg, *args, **kwargs))

    return rule


class ScoreTuple(NamedTuple):
    holder: str
    obj: str


class DataTuple(NamedTuple):
    type: DataTargetType
    target: str
    path: Path


class StringDataTuple(NamedTuple):
    type: DataTargetType
    target: str
    path: Path
    range: tuple[int, int | None]


SourceTuple = ScoreTuple | DataTuple | StringDataTuple


@dataclass
class TempScoreManager:
    objective: str
    prefix: str

    counter: int
    format: Callable[[int], str]

    def __init__(
        self, objective: str, prefix: str, format: Callable[[int], str] | None = None
    ):
        self.objective = objective
        self.prefix = prefix
        self.format = format if format is not None else lambda n: f"{self.prefix}{n}"
        self.counter = 0

    def __call__(self) -> ScoreTuple:
        name = self.format(self.counter)
        self.counter += 1

        return ScoreTuple(name, self.objective)

    @contextmanager
    def override(self, format: Callable[[int], str] | None = None, reset: bool = False):
        counter = self.counter
        if reset:
            self.counter = 0

        prev_format = self.format
        if format:
            self.format = format

        yield

        self.counter = counter
        self.format = prev_format


@dataclass
class TempDataManager:
    target_type: DataTargetType
    target: str

    counter: int = field(default=0, init=False)
    format: Callable[[int], str] = field(default=lambda n: f"i{n}")  # type: ignore

    def __call__(self) -> DataTuple:
        name = self.format(self.counter)
        self.counter += 1

        return DataTuple(self.target_type, self.target, Path(name))

    @contextmanager
    def override(self, format: Callable[[int], str] | None = None, reset: bool = False):
        counter = self.counter
        if reset:
            self.counter = 0

        prev_format = self.format
        if format:
            self.format = format

        yield

        self.counter = counter
        self.format = prev_format


@dataclass
class ConstScoreManager:
    objective: str
    prefix: str

    constants: set[int] = field(default_factory=set, init=False)

    def format(self, value: int) -> str:
        return f"{self.prefix}{value}"

    def create(self, value: int) -> ScoreTuple:
        self.constants.add(value)

        return ScoreTuple(self.format(value), self.objective)

    __call__ = create


@dataclass
class Optimizer:
    """Handles the operation of various optimization rules.

    The `Optimizer.rule` decorates generator functions which process Operation nodes. Each rule
    must take and return a generator of Operation nodes. This usually involves a loop which
    steps through the generator and performs optimizations across the nodes.

    The optimizer runs the nodes through the rules like a conveyor belt and each rule acts as a worker.
    The rules can perform transformations, take nodes off and add different ones on, or even collect
    all nodes, and put on a completely different set of nodes. This metaphor should be considered when
    writing new rules.
    """

    temp_score: TempScoreManager
    temp_data: TempDataManager
    const_score: ConstScoreManager
    default_floating_nbt_type: str

    temp_sources: set[SourceTuple] = field(default_factory=set)
    defined_sources: set[SourceTuple] = field(default_factory=set)

    rules: list[tuple[str, Rule[IrOperation, []]]] = field(default_factory=list)

    def add_rules(self, index: int | None = None, /, **funcs: Rule[IrOperation, []]):
        """Registers new rules, also converts the decorated generator into a `SmartGenerator`"""

        if index is None:
            index = len(self.rules)

        index = min(len(self.rules), index)

        for name, f in reversed(funcs.items()):
            self.rules.insert(index, (name, f))

    @internal
    def optimize(
        self,
        nodes: Iterable[IrOperation],
        temporaries: Iterable[SourceTuple] = (),
        disable_all: bool = False,
        **rules: bool,
    ) -> tuple[Iterable[IrOperation], set[SourceTuple]]:
        """Performs the optimization by sending all nodes through the rules."""

        active_rules = {name: not disable_all for name, _ in self.rules} | rules

        with self.temp(*temporaries) as temporaries:
            for name, rule in self.rules:
                if not active_rules.get(name):
                    continue

                nodes = tuple(rule(nodes))

            return tuple(nodes), temporaries

    __call__ = optimize

    def add_temp(self, *sources: IrSource | SourceTuple):
        for source in sources:
            if isinstance(source, IrSource):
                source = source.to_tuple()

            self.temp_sources.add(source)

    @contextmanager
    def temp(self, *sources: IrSource | SourceTuple):
        prev_temp = self.temp_sources
        self.temp_sources = self.temp_sources.copy()
        self.add_temp(*sources)

        yield self.temp_sources

        self.temp_sources = prev_temp

    def is_temp(self, source: IrSource | SourceTuple):
        if isinstance(source, IrSource):
            source = source.to_tuple()

        return source in self.temp_sources

    def mark_defined(self, *sources: IrSource | SourceTuple):
        for source in sources:
            if isinstance(source, IrSource):
                source = source.to_tuple()

            self.defined_sources.add(source)

    @contextmanager
    def defined(self, *sources: IrSource | SourceTuple):
        prev_defined = set(self.defined_sources)
        self.mark_defined(*sources)

        yield

        self.defined_sources = prev_defined

    def is_defined(self, source: IrSource | SourceTuple):
        if isinstance(source, IrSource):
            source = source.to_tuple()

        return source in self.defined_sources

    def generate_score(self, temp: bool = True) -> IrScore:
        source = self.temp_score()
        if temp:
            self.add_temp(source)

        return IrScore(holder=source.holder, obj=source.obj)

    def generate_const(self, value: int) -> IrScore:
        holder, obj = self.const_score(value)
        return IrScore(holder=holder, obj=obj)

    def generate_data(self, temp: bool = True) -> IrData:
        source = self.temp_data()
        if temp:
            self.add_temp(source)

        return IrData(type=source.type, target=source.target, path=source.path)


def get_data_source_parents(node: IrData) -> tuple[IrData, ...]:
    path = cast(tuple[Accessor, ...], tuple(node.path))

    return tuple(
        replace(node, path=Path.from_accessors(path[:i]))  # type: ignore
        for i in range(len(path), 0, -1)
    )


def replace_source(
    value: IrSource, replace_map: dict[SourceTuple, IrSource]
) -> IrSource:
    if isinstance(value, IrData):
        value_path = cast(tuple[Accessor, ...], tuple(value.path))

        nodes = get_data_source_parents(value)

        for parent_node in nodes:
            replaced = False
            node = parent_node

            while new_node := replace_map.get(node.to_tuple()):
                node = cast(IrData, new_node)
                replaced = True

            if replaced:
                path = cast(
                    tuple[Accessor, ...],
                    tuple(node.path) + value_path[len(parent_node.path) :],
                )
                return replace(
                    node,
                    path=Path.from_accessors(path),  # type: ignore
                    nbt_type=value.nbt_type,
                )

        return value

    while new_node := replace_map.get(value.to_tuple()):
        value = new_node

    return value


def map_node_sources(node: Any, func: Callable[[IrSource], IrSource]) -> Any:
    if is_op(node):
        store = IrChildren(
            replace(s, value=map_node_sources(s.value, func)) for s in node.store
        )
        if isinstance(node, IrBranch):
            return replace(
                node,
                target=map_node_sources(node.target, func),
                store=store,
                children=IrChildren(map_node_sources(ch, func) for ch in node.children),
            )
        if is_unary(node):
            return replace(
                node, store=store, target=map_node_sources(node.target, func)
            )
        if is_binary(node):
            return replace(
                node,
                store=store,
                left=map_node_sources(node.left, func),
                right=map_node_sources(node.right, func),
            )

    if isinstance(node, IrUnaryCondition):
        return replace(node, target=map_node_sources(node.target, func))

    if isinstance(node, IrBinaryCondition):
        return replace(
            node,
            left=map_node_sources(node.left, func),
            right=map_node_sources(node.right, func),
        )

    if isinstance(node, IrSource):
        return func(node)

    return node


def path_accessors(path: Path) -> tuple[Accessor, ...]:
    return cast(tuple[Accessor, ...], tuple(path))


def is_path_child_of(child: Path, parent: Path) -> bool:
    child_accessors = [
        ac for ac in path_accessors(child) if not isinstance(ac, CompoundMatch)
    ]
    parent_accessors = [
        ac for ac in path_accessors(parent) if not isinstance(ac, CompoundMatch)
    ]

    if len(parent_accessors) > len(child_accessors):
        return False

    for child_accessor, parent_accessor in zip(child_accessors, parent_accessors):
        if child_accessor != parent_accessor:
            return False

    return True


def get_parent_paths(path: Path) -> Iterable[Path]:
    accessors = path_accessors(path)

    return tuple(
        Path.from_accessors(accessors[:i])  # type: ignore
        for i in range(len(accessors) - 1, 0, -1)
    )


def get_source_definitions(
    nodes: Iterable[IrOperation],
    ignore_parent: bool = False,
    ignore_children: bool = False,
) -> dict[SourceTuple, list[int]]:
    direct_definitions: dict[SourceTuple, list[int]] = {}

    for i, node in enumerate(nodes):
        for target in node.targets:
            defs = direct_definitions.setdefault(target.to_tuple(), [])
            defs.append(i)

    if ignore_parent and ignore_children:
        return direct_definitions

    definitions = {source: list(defs) for source, defs in direct_definitions.items()}

    if not ignore_children:
        # modifying child path implies in modifying the parent path
        for source in direct_definitions:
            if not isinstance(source, (DataTuple, StringDataTuple)):
                continue

            for parent_path in get_parent_paths(source.path):
                parent_source = DataTuple(source.type, source.target, parent_path)
                parent_defs = definitions.setdefault(parent_source, [])
                parent_defs.extend(
                    i for i in definitions[source] if i not in parent_defs
                )

    if not ignore_parent:
        # modifying parent path implies in modifying child paths
        for parent_source, parent_defs in direct_definitions.items():
            if not isinstance(parent_source, DataTuple):
                continue

            children_sources = [
                source
                for source in direct_definitions
                if isinstance(source, DataTuple)
                and is_path_child_of(source.path, parent_source.path)
            ]
            for source in children_sources:
                definitions[source].extend(
                    i for i in parent_defs if i not in definitions[source]
                )

    return definitions


def get_reaching_definition(
    defs: dict[SourceTuple, list[int]], source: SourceTuple, i: int
) -> int | None:
    source_defs = defs.get(source)
    if source_defs is None:
        return None

    value = bisect_left(source_defs, i) - 1
    return source_defs[value] if value >= 0 else None


def get_node_operand_dependencies(node: IrNode) -> tuple[IrSource, ...]:
    result: list[IrSource] = []

    if is_op(node):
        for operand in node.operands:
            result.extend(get_node_operand_dependencies(operand))
    elif is_unary_condition(node):
        result.extend(get_node_operand_dependencies(node.target))
    elif is_binary_condition(node):
        result.extend(get_node_operand_dependencies(node.left))
        result.extend(get_node_operand_dependencies(node.right))
    elif isinstance(node, IrSource):
        result.append(node)

    return tuple(result)


def get_node_target_dependencies(node: IrOperation) -> set[SourceTuple]:
    dependencies: set[SourceTuple] = set()

    for target in node.targets:
        if isinstance(target, IrData):
            dependencies.update(
                DataTuple(target.type, target.target, path)
                for path in get_parent_paths(target.path)
            )

    return dependencies


def get_node_dependencies(node: IrOperation) -> set[SourceTuple]:
    dependencies = set(
        source.to_tuple() for source in get_node_operand_dependencies(node)
    )
    return dependencies | get_node_target_dependencies(node)


DependencyGraph = tuple[dict[SourceTuple, set[int]], ...]


def get_dependency_graph(nodes: Iterable[IrOperation]) -> DependencyGraph:
    nodes = tuple(nodes)
    result: list[dict[SourceTuple, set[int]]] = []

    defs = get_source_definitions(nodes)
    outward_defs = get_source_definitions(nodes, ignore_children=True)

    for node_i, node in enumerate(nodes):
        dependencies: dict[SourceTuple, set[int]] = {}

        for source in get_node_operand_dependencies(node):
            source_tuple = source.to_tuple()
            dependency_set = dependencies.setdefault(source_tuple, set())
            def_i = node_i

            while True:
                def_i = get_reaching_definition(defs, source_tuple, def_i)

                if def_i is None:
                    break

                dependency_set.add(def_i)
                def_node_dependencies = get_node_dependencies(nodes[def_i])

                if source_tuple not in def_node_dependencies:
                    break

        for source_tuple in get_node_target_dependencies(node):
            def_i = get_reaching_definition(outward_defs, source_tuple, node_i)
            dependency_set = dependencies.setdefault(source_tuple, set())

            if def_i is None:
                continue

            while True:
                dependency_set.add(def_i)
                def_node_dependencies = get_node_dependencies(nodes[def_i])

                if source_tuple not in def_node_dependencies:
                    break

                def_i = get_reaching_definition(defs, source_tuple, def_i)

                if def_i is None:
                    break

        result.append(dependencies)

    return tuple(result)


Location = tuple[int, ...]


def get_source_usage(nodes: Iterable[IrOperation]) -> dict[SourceTuple, set[int]]:
    nodes = tuple(nodes)
    usage: dict[SourceTuple, set[int]] = {}

    for i, node in enumerate(nodes):
        for source in get_node_operand_dependencies(node):
            uses = usage.setdefault(source.to_tuple(), set())
            uses.add(i)

        if isinstance(node, IrBranch):
            inner_usage = get_source_usage(node.children)

            for source, inner_uses in inner_usage.items():
                if inner_uses:
                    uses = usage.setdefault(source, set())
                    uses.add(i)

    for node in nodes:
        for target in (*node.targets, *node.operands):
            if not isinstance(target, IrSource):
                continue

            uses = usage.setdefault(target.to_tuple(), set())

            if not isinstance(target, IrData):
                continue

            for path in get_parent_paths(target.path):
                parent = DataTuple(target.type, target.target, path)

                if parent_uses := usage.get(parent):
                    uses.update(parent_uses)

    for i, node in enumerate(nodes):
        for source in get_node_target_dependencies(node):
            if uses := usage.get(source):
                uses.add(i)

    return usage


def get_source_usage_of_parent(
    usage: dict[SourceTuple, set[int]], parent: SourceTuple
) -> set[int]:
    if not isinstance(parent, (DataTuple, StringDataTuple)):
        return usage.get(parent, set())

    uses: set[int] = set()

    for source in usage:
        if not isinstance(source, (DataTuple, StringDataTuple)):
            continue

        if not is_path_child_of(source.path, parent.path):
            continue

        source_uses = usage.get(source, set())
        uses.update(source_uses)

    return uses


def get_source_usage_old(nodes: Iterable[IrNode]) -> dict[SourceTuple, list[Location]]:
    map: dict[SourceTuple, list[Location]] = {}

    def add(source: Any, i: Location):
        if isinstance(source, (IrSource, SourceTuple)):
            if isinstance(source, IrSource):
                source = source.to_tuple()

            indexes = map.setdefault(source, [])
            indexes.append(i)
        elif isinstance(source, IrUnaryCondition):
            add(source.target, i)
        elif isinstance(source, IrBinaryCondition):
            add(source.left, i)
            add(source.right, i)

    for i, node in enumerate(nodes):
        if not is_op(node):
            continue

        for s in node.store:
            add(s.value, (i,))

        if is_binary(node) and node.store:
            add(node.left, (i,))

        for operand in node.operands:
            add(operand, (i,))

        if isinstance(node, IrBranch):
            children_usage = get_source_usage_old(node.children)
            for source, usage in children_usage.items():
                for u in usage:
                    add(source, (i, *u))

    return map


def data_insert_score(nodes: Iterable[IrOperation]) -> Iterable[IrOperation]:
    for node in nodes:
        if (
            is_binary(node, ("append", "prepend", "insert"))
            and isinstance(node.left, IrData)
            and isinstance(node.right, IrScore)
        ):
            yield replace(node, right=IrLiteral(value=Int(0)))

            if isinstance(node, IrInsert):
                index = node.index
            elif node.op == "prepend":
                index = 0
            else:
                index = -1

            element = replace(node.left, path=node.left.path[index])
            yield IrSet(left=element, right=node.right)
        else:
            yield node


def convert_data_arithmetic(opt: Optimizer, nodes: Iterable[IrOperation]):
    for node in nodes:
        if (
            is_binary(node, SCORE_OPERATIONS)
            and not is_binary(node, DATA_OPERATIONS)
            and isinstance(node.right, IrData)
        ):
            temp_score = opt.generate_score()

            yield IrCast(left=temp_score, right=node.right, cast_type=Int)
            yield replace(node, right=temp_score)

            continue

        yield node


def convert_cast(nodes: Iterable[IrOperation]) -> Iterable[IrOperation]:
    for node in nodes:
        if is_binary(node, "set") and (
            isinstance(node.left, IrScore)
            and isinstance(node.right, IrData)
            or isinstance(node.left, IrData)
            and isinstance(node.right, IrScore)
        ):
            cast_type = Int if isinstance(node.left, IrScore) else Any
            yield IrCast(left=node.left, right=node.right, cast_type=cast_type)
            continue

        yield node


@use_smart_generator
def noncommutative_set_collapsing(nodes: SmartGenerator[IrOperation]):
    """For noncommutative operations:
    ```
    scoreboard players operation $i1 temp = @s rx.uid
    scoreboard players operation $i1 temp -= $i0 temp
    scoreboard players operation @s rx.uid = $i1 temp
    ```

    ->
    ```
    scoreboard players operation @s rx.uid -= $i0 temp
    ```

    Examples to try:
    >>> abc["#value"] -= (1 + abc["@s"])    # doctest: +SKIP
    >>> abc["@s"] *= abc["@s"]              # doctest: +SKIP
    """

    for node in nodes:
        next_node = next(nodes, None)
        further_node = next(nodes, None)
        if (
            is_copy_op(node)
            and is_binary(next_node, SCORE_OPERATIONS)
            and is_copy_op(further_node)
            and isinstance(further_node.left, IrScore)
            and node.right == further_node.left
            and node.left == next_node.left
            and node.left == further_node.right
        ):
            yield replace(next_node, left=further_node.left, right=next_node.right)
        else:
            nodes.push(further_node)
            nodes.push(next_node)
            yield node


@use_smart_generator
def commutative_set_collapsing(
    nodes: SmartGenerator[IrOperation],
) -> Iterable[IrOperation]:
    """For commutative operations:
    ```
    scoreboard players operation $i1 temp += $i0 temp
    scoreboard players operation $i0 temp = $i1 temp
    ```
    Becomes:
    ```
    scoreboard players operation $i0 temp += $i1 temp
    ```
    """
    for node in nodes:
        next_node: Union[IrOperation, None] = next(nodes, None)

        if (
            is_binary(node, ("add", "mul"))
            and is_binary(next_node, "set")
            and isinstance(next_node.left, IrScore)
            and node.left == next_node.right
            and node.right == next_node.left
        ):
            yield replace(node, left=next_node.left, right=next_node.right)
        else:
            nodes.push(next_node)
            yield node


@use_smart_generator
def data_set_scaling(
    nodes: SmartGenerator[IrOperation], opt: Optimizer
) -> Iterable[IrOperation]:
    """
    Turns a multiplication/division of a temp score followed by a
    data set operation into a single set operation with a scale argument.
    ```
    scoreboard players operation $i0 temp /= $100 const
    execute store result storage demo out int 1 run scoreboard players get $i0 temp
    ```
    ->
    ```
    execute store result storage demo out float 0.01 run scoreboard players get $i0 temp
    ```

    Also works with all data operations such as append, prepend and insert:
    ```
    scoreboard players operation $i1 bolt.expr.temp *= $100 bolt.expr.const
    data modify storage demo list append value 0
    execute store result storage demo list[-1] int 1 run scoreboard players get $i1 bolt.expr.temp
    ```
    ->
    ```
    data modify storage demo list append value 0
    execute store result storage demo list[-1] int 100 run scoreboard players get $i1 bolt.expr.temp

    ```
    Examples to try:
    >>> temp.out = (obj["$value"] + 1) * 10
    >>> temp.percent = (obj["$stack"] * 100) / 64
    """
    for node in nodes:
        operation_node = None
        next_node = next(nodes, None)
        # skip data operation node (just so we can get to
        # the actual Set node)
        if is_binary(next_node, ("insert", "append", "prepend")):
            operation_node = next_node
            next_node = next(nodes, None)
        if (
            is_binary(node, ("mul", "div"))
            and isinstance(next_node, IrCast)
            and isinstance(node.right, IrLiteral)
            and isinstance(node.right.value, Numeric)
            and isinstance(next_node.left, IrData)
            and node.left == next_node.right
        ):
            scale = float(node.right.value)

            if scale.is_integer():
                scale = int(scale)

            number_type = next_node.cast_type

            if is_binary(node, "div"):
                scale = 1 / scale

                if number_type is Any:
                    number_type = literal_types[opt.default_floating_nbt_type]

            out = IrCast(
                left=next_node.left, right=node.left, cast_type=number_type, scale=scale
            )

            if operation_node:
                yield operation_node  # yield the data operation node back in

            yield out
        else:
            nodes.push(next_node)
            nodes.push(operation_node)
            yield node


@use_smart_generator
def data_get_scaling(nodes: SmartGenerator[IrOperation]) -> Iterable[IrOperation]:
    """
    ````
    execute store result score $i0 temp run data get storage demo value 1
    scoreboard players operation $i0 temp *= $100 const
    ```
    ->
    ```
    execute store result score $i0 temp run data get storage demo value 100
    ```
    Examples to try:
    >>> obj["#offset"] = (player.Motion[0] * 100) - obj["#x"]
    """
    for node in nodes:
        next_node = next(nodes, None)
        if (
            isinstance(node, IrCast)
            and is_binary(next_node, ("mul", "div"))
            and isinstance(node.right, IrData)
            and isinstance(next_node.right, IrLiteral)
            and isinstance(next_node.right.value, Numeric)
            and node.left == next_node.left
        ):
            scale = float(next_node.right.value)

            if scale.is_integer():
                scale = int(scale)

            if is_binary(next_node, "div"):
                scale = 1 / scale

            yield IrCast(left=node.left, right=node.right, scale=node.scale * scale)
        else:
            nodes.push(next_node)
            yield node


def multiply_divide_by_fraction(nodes: Iterable[IrOperation]):
    for node in nodes:
        if (
            is_binary(node, ("mul", "div"))
            and isinstance(node.right, IrLiteral)
            and isinstance(node.right.value, (Float, Double))
        ):
            value = Fraction(node.right.value).limit_denominator()

            if is_binary(node, "div"):
                value = 1 / value

            numerator = IrLiteral(value=Int(value.numerator))
            denominator = IrLiteral(value=Int(value.denominator))

            yield IrBinary(op="mul", left=node.left, right=numerator)
            yield IrBinary(op="div", left=node.left, right=denominator)
        else:
            yield node


def multiply_divide_by_one_removal(nodes: Iterable[IrOperation]):
    for node in nodes:
        if not (
            is_binary(node, ("mul", "div"))
            and isinstance(node.right, IrLiteral)
            and node.right.value == 1
        ):
            yield node


def add_subtract_by_zero_removal(nodes: Iterable[IrOperation]):
    for node in nodes:
        if not (
            is_binary(node, ("add", "sub"))
            and isinstance(node.right, IrLiteral)
            and node.right.value == 0
        ):
            yield node


def discard_casting(nodes: Iterable[IrOperation]) -> Iterable[IrOperation]:
    for node in nodes:
        if isinstance(node, IrCast) and is_copy_op(node):
            yield IrSet(left=node.left, right=node.right)
        else:
            yield node


def discard_non_numerical_casting(
    nodes: Iterable[IrOperation],
) -> Iterable[IrOperation]:
    for node in nodes:
        if (
            isinstance(node, IrCast)
            and isinstance(node.left, IrData)
            and isinstance(node.right, IrData)
            and node.scale == 1
            and not is_numeric_type(unwrap_optional_type(node.cast_type))
        ):
            yield IrSet(left=node.left, right=node.right)
        else:
            yield node


def set_to_self_removal(nodes: Iterable[IrOperation]):
    """Removes Set operations that have the same former and latter source.
    Should run after "output_score_replacement" is applied to clean up
    all the reduntant Sets created by the previous rule.
    """
    for node in nodes:
        if is_copy_op(node):
            if (
                not isinstance(node.right, IrSource)
                or type(node.left) is not type(node.right)
                or node.left.to_tuple() != node.right.to_tuple()
            ):
                yield node
        else:
            yield node


def literal_to_constant_replacement(
    opt: Optimizer,
    nodes: Iterable[IrOperation],
) -> Iterable[IrOperation]:
    for node in nodes:
        if (
            is_binary(node, ("mul", "div", "min", "max", "mod"))
            and isinstance(node.right, IrLiteral)
            and isinstance(node.right.value, Numeric)
        ):
            value = int(node.right.value)
            constant = opt.generate_const(value)

            yield replace(node, right=constant)
        else:
            yield node


def set_and_get_cleanup(nodes: Iterable[IrOperation]) -> Iterable[IrOperation]:
    """
    Removes unnecessary temp vars possibly originated from previous
    optimizations.
    ```
    scoreboard players operation $i0 bolt.expr.temp = $value obj
    execute store result storage demo out float 0.01 run scoreboard players get $i0 bolt.expr.temp
    ```
    ->
    ```
    execute store result storage demo out float 0.01 run scoreboard players get $value obj
    ```
    Examples to try:
    >>> temp.out = obj["$value"] / 100
    >>> temp.out = temp.value * 100 / 100
    """

    nodes = tuple(nodes)
    usage = get_source_usage(nodes)
    definitions = get_source_definitions(nodes)

    operations: list[IrOperation] = []

    for node_i, node in enumerate(nodes):
        operands: list[OperandType] = []

        for operand in node.operands:
            operands.append(operand)

            if not isinstance(operand, IrSource):
                continue

            source = operand.to_tuple()
            def_i = get_reaching_definition(definitions, source, node_i)

            if def_i is None:
                continue

            def_node = nodes[def_i]

            if (
                not isinstance(def_node, (IrSet, IrCast))
                or not isinstance(def_node.right, IrSource)
                or def_node.left.to_tuple() != source
                or operand in node.targets
            ):
                continue

            if isinstance(def_node, IrCast) and (
                def_node.scale != 1.0
                or not isinstance(def_node.left, IrScore)
                or not isinstance(node, (IrSet, IrCast))
            ):
                continue

            if any(
                def_i < use_i < node_i
                for use_i in get_source_usage_of_parent(usage, source)
            ):
                continue

            operands[-1] = def_node.right

        operations.append(replace_operation(node, operands=operands))

    yield from convert_cast(operations)


def rename_temp_scores(
    opt: Optimizer,
    nodes: Iterable[IrOperation],
) -> Iterable[IrOperation]:
    nodes = tuple(nodes)

    ignored_sources: set[IrSource] = set()

    defs = get_source_definitions(nodes, ignore_parent=True, ignore_children=True)
    for i, node in enumerate(nodes):
        for source in get_node_operand_dependencies(node):
            source_defs = defs.get(source.to_tuple(), [])

            if not any(def_i < i for def_i in source_defs):
                ignored_sources.add(source)

    with (
        opt.temp_score.override(
            format=lambda n: f"{opt.temp_score.prefix}i{n}", reset=True
        ),
        opt.temp_data.override(format=lambda n: f"i{n}", reset=True),
    ):
        replace_map: dict[SourceTuple, IrSource] = {}

        def map_source(node: IrSource) -> IrSource:
            if node in ignored_sources:
                return node

            replaced_node = replace_source(node, replace_map)

            if replaced_node != node:
                return replaced_node

            if not opt.is_temp(node):
                return node

            node_tuple = node.to_tuple()

            if isinstance(node, IrScore):
                replace_map[node_tuple] = opt.generate_score()
            elif isinstance(node, IrData):
                replace_map[node_tuple] = opt.generate_data()
            else:
                replace_map[node_tuple] = node

            return replace_map[node_tuple]

        nodes = [map_node_sources(node, map_source) for node in nodes]

    yield from nodes


def data_string_propagation(nodes: Iterable[IrOperation]) -> Iterable[IrOperation]:
    all_nodes = tuple(nodes)
    defs = get_source_definitions(all_nodes)

    for i, node in enumerate(all_nodes):
        if not is_binary(
            node, ("append", "prepend", "merge", "insert", "set")
        ) or not isinstance(node.right, IrSource):
            yield node
            continue

        cond_def_i = get_reaching_definition(defs, node.right.to_tuple(), i)
        if cond_def_i is None:
            yield node
            continue

        cond_def = all_nodes[cond_def_i]

        if (
            is_binary(cond_def, "set")
            and isinstance(cond_def.right, IrDataString)
            and cond_def.left.to_tuple() == node.right.to_tuple()
        ):
            yield replace(node, right=cond_def.right)
            continue

        yield node


def negate_condition(node: IrCondition):
    if is_unary_condition(node, "not"):
        return IrUnaryCondition(op="truthy", target=node.target)

    return replace(node, negated=not node.negated)


def boolean_condition_propagation(
    nodes: Iterable[IrOperation],
) -> Iterable[IrOperation]:
    all_nodes = list(nodes)
    defs = get_source_definitions(all_nodes)

    for i, node in enumerate(all_nodes):
        if is_binary(node, "set") and is_unary_condition(node.right, "boolean"):
            bool_cond = node.right

            cond_def_i = get_reaching_definition(defs, bool_cond.target.to_tuple(), i)
            if cond_def_i is None:
                continue

            cond_node = all_nodes[cond_def_i]

            if (
                is_binary(cond_node, "set")
                and is_condition(cond_node.right)
                and cond_node.left.to_tuple() == bool_cond.target.to_tuple()
            ):
                right = (
                    negate_condition(cond_node.right)
                    if bool_cond.negated
                    else cond_node.right
                )
                all_nodes[i] = replace(node, right=right)

    yield from all_nodes


def branch_condition_propagation(nodes: Iterable[IrOperation]) -> Iterable[IrOperation]:
    all_nodes = tuple(nodes)
    defs = get_source_definitions(all_nodes)

    for i, node in enumerate(all_nodes):
        if not is_unary(node, "branch") or not isinstance(node.target, IrSource):
            yield node
            continue

        cond_def_i = get_reaching_definition(defs, node.target.to_tuple(), i)
        if cond_def_i is None:
            yield node
            continue

        cond_def = all_nodes[cond_def_i]

        if (
            is_binary(cond_def, "set")
            and is_condition(cond_def.right)
            and node.target.to_tuple() == cond_def.left.to_tuple()
        ):
            yield replace(node, target=cond_def.right)
            continue

        yield node


def deadcode_elimination(
    nodes: Iterable[IrOperation], opt: Optimizer
) -> Iterable[IrOperation]:
    all_nodes = tuple(nodes)
    usage = get_source_usage_old(all_nodes)

    for node_i, node in enumerate(all_nodes):
        if isinstance(node, IrBranch):
            yield node
            continue

        store: list[IrStore] = []

        for store_el in node.store:
            source = store_el.value

            if not opt.is_temp(source) or any(
                use_i > (node_i,) for use_i in usage.get(source.to_tuple(), [])
            ):
                store.append(store_el)

        if store != node.store:
            node = replace(node, store=IrChildren(store))

        for target in node.targets:
            if not opt.is_temp(target):
                yield node
                break

            target_usage = usage.get(target.to_tuple(), [])

            if any(use_i > (node_i,) for use_i in target_usage):
                yield node
                break


def convert_data_order_operation(
    nodes: Iterable[IrOperation], opt: Optimizer
) -> Iterable[IrOperation]:
    result: list[IrOperation] = []

    OPERATIONS = (
        "less_than",
        "less_than_or_equal_to",
        "greater_than",
        "greater_than_or_equal_to",
        "equal",
    )

    def replace_operand(node: Any, in_condition: bool = False) -> Any:
        if is_binary_condition(node) and node.op in OPERATIONS:
            return replace(
                node,
                left=replace_operand(node.left, in_condition=True),
                right=replace_operand(node.right, in_condition=True),
            )

        if is_unary_condition(node) and node.op in OPERATIONS:
            return replace(node, target=replace_operand(node.target, in_condition=True))

        if isinstance(node, IrData) and in_condition:
            score = opt.generate_score()
            result.append(IrCast(left=score, right=node, cast_type=Int))
            return score

        return node

    for node in nodes:
        if is_unary(node):
            node = replace(node, target=replace_operand(node.target))
        elif is_binary(node):
            node = replace(
                node, left=replace_operand(node.left), right=replace_operand(node.right)
            )

        result.append(node)

    yield from result


def compound_match_data_compare(
    nodes: Iterable[IrOperation], opt: Optimizer
) -> Iterable[IrOperation]:
    for node in nodes:
        operands: list[OperandType] = []

        for operand in node.operands:
            if (
                is_binary_condition(operand, "equal")
                and isinstance(operand.left, IrData)
                and isinstance(operand.right, IrLiteral)
            ):
                value = operand.right.value

                if not isinstance(value, (Numeric, String)):
                    operands.append(operand)
                    continue

                source = operand.left
                negated = operand.negated
                path = cast(tuple[Accessor, ...], tuple(source.path))
                accessor = path[-1] if len(path) else None
                match = None

                if isinstance(accessor, NamedKey):
                    subpath = path[:-1]
                    match = CompoundMatch(Compound({accessor.key: value}))
                else:
                    temp = opt.generate_data(temp=False)

                    yield IrUnary(op="remove", target=temp)
                    yield IrSet(left=temp, right=source)

                    accessor = cast(NamedKey, tuple(temp.path)[-1])
                    source = temp
                    subpath = ()
                    match = CompoundMatch(Compound({accessor.key: value}))

                new_path = Path.from_accessors((*subpath, match))  # type: ignore
                new_source = replace(source, path=new_path)
                operand = IrUnaryCondition(
                    op="boolean", target=new_source, negated=negated
                )

            operands.append(operand)

        yield replace_operation(node, operands=operands)


def store_set_data_compare(
    nodes: Iterable[IrOperation], opt: Optimizer
) -> Iterable[IrOperation]:
    for node in nodes:
        operands: list[OperandType] = []

        for operand in node.operands:
            if is_binary_condition(operand, "equal"):
                data = operand.left
                value = operand.right

                if not isinstance(data, IrData):
                    data, value = value, data

                if not isinstance(data, IrData) or not isinstance(
                    value, (IrData, IrLiteral)
                ):
                    operands.append(operand)
                    continue

                result = opt.generate_score()
                cmp = opt.generate_data()

                opt.mark_defined(result)
                yield IrSet(left=result, right=IrLiteral(value=Int(1)))
                yield IrSet(left=cmp, right=data)

                store = IrStore(type=StoreType.success, value=result)
                set_op = IrSet(store=IrChildren((store,)), left=cmp, right=value)

                if isinstance(value, IrData):
                    inner_op = IrBranch(
                        target=IrUnaryCondition(op="boolean", target=value),
                        children=IrChildren((set_op,)),
                    )
                else:
                    inner_op = set_op

                yield IrBranch(
                    target=IrUnaryCondition(op="boolean", target=data),
                    children=IrChildren((inner_op,)),
                )

                operand = IrUnaryCondition(op="boolean", target=result, negated=True)

            operands.append(operand)

        yield replace_operation(node, operands=operands)


def init_score_boolean_result(nodes: Iterable[IrOperation]) -> Iterable[IrOperation]:
    all_nodes = tuple(nodes)
    defs = get_source_definitions(all_nodes)

    for i, node in enumerate(all_nodes):
        if (
            is_binary(node, "set")
            and is_unary_condition(node.right, "boolean")
            and isinstance(node.right.target, IrScore)
            and not any(x < i for x in defs.get(node.left.to_tuple(), []))
        ):
            yield IrSet(left=node.left, right=IrLiteral(value=Int(0)))

        yield node


Op = TypeVar("Op", bound=IrOperation)


def replace_operation(
    node: Op, operands: Iterable[OperandType] | None = None, **kwargs: Any
) -> Op:
    if operands is None:
        operands = node.operands
    else:
        operands = tuple(operands)

    if is_unary(node):
        return replace(node, target=operands[0], **kwargs)

    if is_binary(node):
        if len(operands) == 1:
            return replace(node, right=operands[0], **kwargs)

        return replace(node, left=operands[0], right=operands[1], **kwargs)

    return replace(node, **kwargs)


def convert_defined_boolean_condition(
    nodes: Iterable[IrOperation], opt: Optimizer
) -> Iterable[IrOperation]:
    for node in nodes:
        operands: list[OperandType] = []

        for operand in node.operands:
            if is_unary(node, "branch") and isinstance(operand, IrSource):
                operand = IrUnaryCondition(op="boolean", target=operand)

            if (
                is_unary_condition(operand, "boolean")
                and isinstance(operand.target, IrScore)
                and opt.is_defined(operand.target)
            ):
                negated = not operand.negated
                target = operand.target
                zero = IrLiteral(value=Int(0))

                operand = IrBinaryCondition(
                    op="equal", left=target, right=zero, negated=negated
                )

            operands.append(operand)

        yield replace_operation(node, operands=tuple(operands))


def store_result_inlining(nodes: Iterable[IrOperation]) -> Iterable[IrOperation]:
    nodes = tuple(nodes)

    defs = get_source_definitions(nodes)

    stores: dict[int, list[IrStore]] = {}
    removed: set[int] = set()

    for i, node in enumerate(nodes):
        if not isinstance(node, IrCast) or not isinstance(node.right, IrSource):
            continue

        source_def_i = get_reaching_definition(defs, node.right.to_tuple(), i)

        if source_def_i is None or source_def_i != (i - 1):
            continue

        def_node = nodes[source_def_i]

        if isinstance(def_node, (IrSet, IrCast)):
            continue

        store = IrStore(
            type=StoreType.result,
            value=node.left,
            cast_type=node.cast_type,
            scale=node.scale,
        )
        source_stores = stores.setdefault(source_def_i, [])
        source_stores.append(store)
        removed.add(i)

    for i, node in enumerate(nodes):
        if store := stores.get(i):
            node = replace(node, store=IrChildren((*node.store, *store)))

        if i not in removed:
            yield node


def get_default_value(type: NbtType) -> NbtValue:
    type = unwrap_optional_type(type)

    if is_numeric_type(type):
        return type(0)

    if is_string_type(type):
        return String("")

    if is_list_type(type):
        return List([])

    if is_array_type(type):
        return type([])

    if is_compound_type(type):
        return Compound({})

    return Int(0)


def traverse_composite_literal(
    value: CompositeNbtValue,
    result: IrData,
    type: NbtType,
    ctx: Context,
    operations: list[IrOperation],
) -> NbtValue:
    literal: Any

    if isinstance(value, dict):
        value = cast(dict[str, CompositeNbtValue | IrSource], value)

        literal = {}

        for key, val in value.items():
            val_result = replace(result, path=result.path[key])

            if isinstance(val, IrSource):
                accessors = cast(tuple[Accessor, ...], tuple(val_result.path))
                cast_type = access_type_by_path(type, accessors[1:], ctx)

                if cast_type in (None, Any):
                    cast_type = val.nbt_type if isinstance(val, IrData) else Any

                operations.append(
                    IrCast(left=val_result, right=val, cast_type=cast_type or Any)
                )
                nbt_val = get_default_value(cast_type)
            else:
                nbt_val = traverse_composite_literal(
                    val, val_result, type, ctx, operations
                )

            literal[key] = nbt_val

    elif isinstance(value, list):
        value = cast(list[CompositeNbtValue | IrSource], value)

        literal = []

        accessors = cast(tuple[Accessor, ...], tuple(result.path[0]))
        cast_type = access_type_by_path(type, accessors[1:], ctx)

        if cast_type in (None, Any):
            literals = [el for el in value if not isinstance(el, IrSource)]

            if literals:
                cast_type = infer_type(literals[0], shallow=True)

            if cast_type in (None, Any):
                data_source_types = [
                    el.nbt_type
                    for el in value
                    if isinstance(el, IrData) and el.nbt_type is not Any
                ]
                cast_type = data_source_types[0] if data_source_types else Int

        for i, val in enumerate(value):
            val_result = replace(result, path=result.path[i])

            if isinstance(val, IrSource):
                operations.append(
                    IrCast(left=val_result, right=val, cast_type=cast_type)
                )
                nbt_val = get_default_value(cast_type)
            else:
                nbt_val = traverse_composite_literal(
                    val, val_result, type, ctx, operations
                )

            literal.append(nbt_val)
    else:
        literal = value

    nbt = convert_tag(literal)

    if nbt is None:
        raise ValueError("Invalid nbt.")

    return nbt


def composite_literal_expansion(
    nodes: Iterable[IrOperation], opt: Optimizer, ctx: Context
) -> Iterable[IrOperation]:
    for node in nodes:
        if not any(
            isinstance(operand, IrCompositeLiteral) for operand in node.operands
        ):
            yield node
            continue

        operands: list[OperandType] = []

        for operand in node.operands:
            if isinstance(operand, IrCompositeLiteral):
                result = opt.generate_data()

                if isinstance(node, IrCast):
                    type = node.cast_type
                elif is_binary(node, ("append", "prepend", "insert")) and isinstance(
                    node.left, IrData
                ):
                    type = (
                        access_type_by_path(node.left.nbt_type, (ListIndex(0),)) or Any
                    )
                else:
                    type = Any

                operations: list[IrOperation] = []
                nbt_value = traverse_composite_literal(
                    operand.value, result, type, ctx, operations
                )

                yield IrCast(
                    left=result, right=IrLiteral(value=nbt_value), cast_type=type
                )
                yield from operations

                operand = result

            operands.append(operand)

        yield replace_operation(node, operands)


def source_copy_elision(
    nodes: Iterable[IrOperation], opt: Optimizer
) -> Iterable[IrOperation]:
    nodes = list(nodes)
    active = True

    while active:
        active = False

        definitions = get_source_definitions(nodes)
        dependency = get_dependency_graph(nodes)
        usage = get_source_usage(nodes)

        for node_i in range(len(nodes)):
            node = nodes[node_i]
            if not (
                is_binary(node, "set")
                and isinstance(node.right, IrSource)
                and opt.is_temp(node.right)
            ):
                continue

            target = node.left.to_tuple()
            target_source = node.left
            source = node.right.to_tuple()

            if any(
                use_i > node_i for use_i in get_source_usage_of_parent(usage, source)
            ):
                continue

            node_dependencies = dependency[node_i]
            deps = sorted(node_dependencies.get(source, set()))

            if not deps:
                continue

            if any(
                deps[0] < target_use_i < node_i
                for target_use_i in get_source_usage_of_parent(usage, target)
            ):
                continue

            conflicting_defs = sorted(
                def_i
                for def_i in definitions.get(target, [])
                if deps[0] < def_i < node_i
            )
            if conflicting_defs:
                def_i = conflicting_defs[0]

                def_deps = tuple(
                    s for source_deps in dependency[def_i].values() for s in source_deps
                )
                if any(deps[0] < dep_i for dep_i in def_deps):
                    continue

                def_node = nodes.pop(def_i)
                nodes.insert(deps[0], def_node)

                active = True
                break

            for i in deps:
                nodes[i] = map_node_sources(
                    nodes[i], lambda s: replace_source(s, {source: target_source})
                )

            nodes.pop(node_i)

            active = True
            break

    return nodes
