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
)

from .typing import (
    Accessor,
    NbtType,
    NbtValue,
    literal_types,
    unwrap_optional_type,
)

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
    "apply_temp_source_reuse",
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
class IrLiteral(IrNode):
    value: NbtValue


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


SourceTuple = ScoreTuple | DataTuple


@dataclass
class TempScoreManager:
    objective: str

    counter: int = field(default=0, init=False)
    format: Callable[[int], str] = field(default=lambda n: f"$s{n}")  # type: ignore

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

    constants: set[int] = field(default_factory=set, init=False)

    def format(self, value: int) -> str:
        return f"${value}"

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

                nodes = rule(nodes)

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


Location = tuple[int, ...]


def get_source_usage(nodes: Iterable[IrNode]) -> dict[IrSource, list[Location]]:
    map: dict[IrSource, list[Location]] = {}

    def add(source: Any, i: Location):
        if isinstance(source, IrSource):
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

        if is_binary(node):
            if node.op in ("set", "cast") and len(node.store):
                add(node.left, (i,))
            add(node.right, (i,))

        if is_unary(node):
            add(node.target, (i,))

        if isinstance(node, IrBranch):
            children_usage = get_source_usage(node.children)
            for source, usage in children_usage.items():
                for u in usage:
                    add(source, (i, *u))

    return map


def apply_temp_source_reuse(
    opt: Optimizer, nodes: Iterable[IrOperation]
) -> Iterable[IrOperation]:
    all_nodes = list(nodes)

    usage_map = get_source_usage(all_nodes)
    replace_map: dict[IrSource, IrSource] = {}

    def replace_operand(value: Any) -> Any:
        if isinstance(value, IrUnaryCondition):
            return replace(value, target=replace_operand(value.target))

        if isinstance(value, IrBinaryCondition):
            return replace(
                value,
                left=replace_operand(value.left),
                right=replace_operand(value.right),
            )

        if replaced := replace_map.get(value):
            return replace_operand(replaced)

        return value

    for i, node in enumerate(all_nodes):
        if (
            is_binary(node, "set")
            and isinstance(node.right, IrSource)
            and opt.is_temp(node.right)
            and type(node.left) is type(node.right)
        ):
            left_usage = usage_map.get(node.left)
            right_usage = usage_map.get(node.right)

            if right_usage is None:
                continue

            if left_usage is None or left_usage[0] > (i,) and right_usage[-1] == (i,):
                replace_map[node.right] = node.left

    for node in all_nodes:
        store = IrChildren(
            replace(s, value=replace_operand(s.value)) for s in node.store
        )

        if is_unary(node):
            yield replace(node, store=store, target=replace_operand(node.target))
        elif is_binary(node):
            yield replace(
                node,
                store=store,
                left=replace_operand(node.left),
                right=replace_operand(node.right)
                if isinstance(node.right, IrSource)
                else node.right,
            )
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


def set_to_self_removal(nodes: Iterable[IrOperation]):
    """Removes Set operations that have the same former and latter source.
    Should run after "output_score_replacement" is applied to clean up
    all the reduntant Sets created by the previous rule.
    """
    for node in nodes:
        if is_copy_op(node):
            if node.left != node.right:
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


@use_smart_generator
def set_and_get_cleanup(nodes: SmartGenerator[IrOperation]) -> Iterable[IrOperation]:
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
    for node in nodes:
        next_node = next(nodes, None)
        if (
            is_binary(node, ("set", "cast"))
            and is_binary(next_node, ("set", "cast"))
            and node.left == next_node.right
        ):
            scale = 1
            if isinstance(next_node, IrCast):
                scale = next_node.scale

            if isinstance(node, IrCast):
                if node.cast_type is not Any and not isinstance(node.left, IrScore):
                    nodes.push(next_node)
                    yield node
                    continue

                scale *= node.scale

            if isinstance(next_node, IrCast):
                out = replace(next_node, right=node.right, scale=scale)
            else:
                out = replace(next_node, right=node.right)

            yield out
            continue

        nodes.push(next_node)
        yield node


def rename_temp_scores(
    opt: Optimizer,
    nodes: Iterable[IrOperation],
) -> Iterable[IrOperation]:
    nodes = tuple(nodes)

    ignored_sources: set[IrSource] = set()

    defs = get_source_definitions(nodes)
    for i, node in enumerate(nodes):
        for source in get_node_dependencies(node):
            source_defs = defs.get(source, [])

            if not any(def_i < i for def_i in source_defs):
                ignored_sources.add(source)

    with (
        opt.temp_score.override(format=lambda n: f"$i{n}", reset=True),
        opt.temp_data.override(format=lambda n: f"i{n}", reset=True),
    ):
        source_map: dict[IrSource, IrSource] = {}

        def replace_node(node: Any) -> Any:
            if node in ignored_sources:
                return node

            if is_op(node):
                store = IrChildren(
                    replace(s, value=replace_node(s.value)) for s in node.store
                )
                if isinstance(node, IrBranch):
                    return replace(
                        node,
                        target=replace_node(node.target),
                        store=store,
                        children=IrChildren(replace_node(ch) for ch in node.children),
                    )
                if is_unary(node):
                    return replace(node, store=store, target=replace_node(node.target))
                if is_binary(node):
                    return replace(
                        node,
                        store=store,
                        left=replace_node(node.left),
                        right=replace_node(node.right),
                    )

            if isinstance(node, IrUnaryCondition):
                return replace(node, target=replace_node(node.target))

            if isinstance(node, IrBinaryCondition):
                return replace(
                    node,
                    left=replace_node(node.left),
                    right=replace_node(node.right),
                )

            if isinstance(node, IrSource):
                if not opt.is_temp(node):
                    return node

                if node not in source_map:
                    if isinstance(node, IrScore):
                        source_map[node] = opt.generate_score()
                    elif isinstance(node, IrData):
                        source_map[node] = opt.generate_data()
                    else:
                        source_map[node] = node

                return source_map[node]

            return node

        for node in nodes:
            yield replace_node(node)


def get_source_definitions(nodes: Iterable[IrOperation]) -> dict[IrSource, list[int]]:
    definitions: dict[IrSource, list[int]] = {}

    for i, node in enumerate(nodes):
        for target in node.targets:
            defs = definitions.setdefault(target, [])
            defs.append(i)

    return definitions


def get_reaching_definition(
    defs: dict[IrSource, list[int]], source: IrSource, i: int
) -> int | None:
    source_defs = defs.get(source)
    if source_defs is None:
        return None

    value = bisect_left(source_defs, i) - 1
    return source_defs[value] if value >= 0 else None


def get_node_dependencies(node: IrNode) -> tuple[IrSource, ...]:
    result: list[IrSource] = []

    if is_op(node):
        for operand in node.operands:
            result.extend(get_node_dependencies(operand))
    elif is_unary_condition(node):
        result.extend(get_node_dependencies(node.target))
    elif is_binary_condition(node):
        result.extend(get_node_dependencies(node.left))
        result.extend(get_node_dependencies(node.right))
    elif isinstance(node, IrSource):
        result.append(node)

    return tuple(result)


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

            cond_def_i = get_reaching_definition(defs, bool_cond.target, i)
            if cond_def_i is None:
                continue

            cond_node = all_nodes[cond_def_i]

            if is_binary(cond_node, "set") and is_condition(cond_node.right):
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

        cond_def_i = get_reaching_definition(defs, node.target, i)
        if cond_def_i is None:
            yield node
            continue

        cond_def = all_nodes[cond_def_i]

        if is_binary(cond_def, "set") and is_condition(cond_def.right):
            yield replace(node, target=cond_def.right)
            continue

        yield node


def deadcode_elimination(
    nodes: Iterable[IrOperation], opt: Optimizer
) -> Iterable[IrOperation]:
    all_nodes = tuple(nodes)
    usage = get_source_usage(all_nodes)

    for node_i, node in enumerate(all_nodes):
        if isinstance(node, IrBranch):
            yield node
            continue

        for target in node.targets:
            if not opt.is_temp(target):
                yield node
                continue

            target_usage = usage.get(target, [])

            if any(use_i > (node_i,) for use_i in target_usage):
                yield node
                continue


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
            and not any(x < i for x in defs.get(node.left, []))
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
