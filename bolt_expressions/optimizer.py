from dataclasses import dataclass, field, replace
from fractions import Fraction
from types import TracebackType
from typing import (
    Any,
    Callable,
    Generator,
    Iterable,
    Iterator,
    Literal,
    NamedTuple,
    TypeGuard,
    TypeVar,
    Union,
    Concatenate,
    ParamSpec,
)
from mecha import AbstractNode

from nbtlib import (
    Int,
    Double,
    Float,
    Numeric,
    Path,
)  # type:ignore

from .typing import NbtType, NbtValue, unwrap_optional_type, is_numeric_type

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
    "StoreValue",
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


@dataclass(frozen=True, kw_only=True)
class IrSource(IrNode):
    temp: bool = False


@dataclass(frozen=True, kw_only=True)
class IrScore(IrSource):
    holder: str
    obj: str


DataTargetType = Literal["storage", "entity", "block"]


@dataclass(frozen=True, kw_only=True)
class IrData(IrSource):
    type: DataTargetType
    target: str
    path: Path
    nbt_type: NbtType = Any
    scale: float | None = None


@dataclass(frozen=True, kw_only=True)
class IrLiteral(IrNode):
    value: NbtValue


StoreValue = tuple[Literal["result", "success"], IrSource]


@dataclass(frozen=True, kw_only=True)
class IrOperation(IrNode):
    op: str
    store: tuple[StoreValue, ...] = ()


@dataclass(frozen=True, kw_only=True)
class IrUnary(IrOperation):
    target: IrSource


@dataclass(frozen=True, kw_only=True)
class IrBinary(IrOperation):
    left: IrSource
    right: IrSource | IrLiteral


@dataclass(frozen=True, kw_only=True)
class IrInsert(IrBinary):
    op: str = field(default="insert", init=False)
    index: int


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


def is_cast_op(node: IrBinary) -> bool:
    if node.op != "set":
        return False

    if not isinstance(node.left, IrData):
        return False
    if not isinstance(node.right, IrData):
        return False

    left_scale = node.left.scale
    if left_scale is not None and left_scale != 1:
        return True

    right_scale = node.right.scale
    if right_scale is not None and right_scale != 1:
        return True

    left_type = unwrap_optional_type(node.left.nbt_type)
    right_type = unwrap_optional_type(node.right.nbt_type)

    if left_type is Any:
        return False

    if not is_numeric_type(left_type):
        return False

    return left_type != right_type


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
    nbt_type: NbtType = Any


@dataclass
class TempScoreManager:
    objective: str

    counter: int = field(default=0, init=False)

    def __call__(self) -> ScoreTuple:
        name = f"$i{self.counter}"
        self.counter += 1

        return ScoreTuple(name, self.objective)

    def reset(self):
        self.counter = 0


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
    const_score: ConstScoreManager
    default_floating_nbt_type: str

    rules: list[Rule[IrOperation, []]] = field(default_factory=list)

    def add_rules(self, *funcs: Rule[IrOperation, []], index: int | None = None):
        """Registers new rules, also converts the decorated generator into a `SmartGenerator`"""

        if index is None:
            index = len(self.rules)

        index = min(len(self.rules), index)

        for f in funcs[::-1]:
            self.rules.insert(index, f)

    def optimize(self, nodes: Iterable[IrOperation]) -> Iterable[IrOperation]:
        """Performs the optimization by sending all nodes through the rules."""

        for rule in self.rules:
            nodes = rule(nodes)

        yield from nodes

    __call__ = optimize

    def generate_score(self) -> IrScore:
        holder, obj = self.temp_score()
        return IrScore(holder=holder, obj=obj, temp=True)

    def generate_const(self, value: int) -> IrScore:
        holder, obj = self.const_score(value)
        return IrScore(holder=holder, obj=obj)


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
            yield IrBinary(op="set", left=element, right=node.right)
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

            yield IrBinary(op="set", left=temp_score, right=node.right)
            yield replace(node, right=temp_score)

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
            is_binary(node, "set")
            and is_binary(next_node, SCORE_OPERATIONS)
            and is_binary(further_node, "set")
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
            # print("old", node)
            nodes.push(next_node)
            yield node


@use_smart_generator
def data_set_scaling(nodes: SmartGenerator[IrOperation], opt: Optimizer):
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
            and is_binary(next_node, "set")
            and isinstance(node.right, IrLiteral)
            and isinstance(node.right.value, Numeric)
            and isinstance(next_node.left, IrData)
            and node.left == next_node.right
        ):
            scale = float(node.right.value)

            if scale.is_integer():
                scale = int(scale)

            source = next_node.left
            number_type = source.nbt_type

            if is_binary(node, "div"):
                scale = 1 / scale

                if number_type is Any:
                    number_type = opt.default_floating_nbt_type

            new_source = replace(source, scale=scale, nbt_type=number_type)
            out = IrBinary(op="set", left=new_source, right=node.left)

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
            is_binary(node, "set")
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

            yield IrBinary(
                op="set", left=node.left, right=replace(node.right, scale=scale)
            )
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


def get_source_usage(nodes: Iterable[IrOperation]) -> dict[IrSource, list[int]]:
    map: dict[IrSource, list[int]] = {}

    def add(source: IrSource, i: int):
        indexes = map.setdefault(source, [])
        indexes.append(i)

    for i, node in enumerate(nodes):
        for _, source in node.store:
            add(source, i)

        if is_binary(node):
            add(node.left, i)

            if isinstance(node.right, IrSource):
                add(node.right, i)

        if is_unary(node):
            add(node.target, i)

    return map


def apply_temp_source_reuse(nodes: Iterable[IrOperation]) -> Iterable[IrOperation]:
    all_nodes = list(nodes)

    usage_map = get_source_usage(all_nodes)
    # print(usage_map)

    replace_map: dict[IrSource, IrSource] = {}

    def replace_source(source: IrSource) -> IrSource:
        if replaced := replace_map.get(source):
            return replace_source(replaced)

        return source

    for i, node in enumerate(all_nodes):
        if (
            is_binary(node, "set")
            and isinstance(node.right, IrSource)
            and node.right.temp
            and type(node.left) is type(node.right)
            and not is_cast_op(node)
        ):
            left_usage = usage_map[node.left]
            right_usage = usage_map[node.right]

            if left_usage[0] == right_usage[-1] == i:
                replace_map[node.right] = node.left

    for node in all_nodes:
        store = tuple((type, replace_source(source)) for type, source in node.store)

        if is_unary(node):
            yield replace(node, store=store, target=replace_source(node.target))
        elif is_binary(node):
            yield replace(
                node,
                store=store,
                left=replace_source(node.left),
                right=replace_source(node.right)
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


def set_to_self_removal(nodes: Iterable[IrOperation]):
    """Removes Set operations that have the same former and latter source.
    Should run after "output_score_replacement" is applied to clean up
    all the reduntant Sets created by the previous rule.
    """
    for node in nodes:
        if is_binary(node, "set"):
            if node.left != node.right:
                yield node
        else:
            yield node


@use_smart_generator
def set_and_get_cleanup(nodes: SmartGenerator[IrOperation]):
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
            is_binary(node, "set")
            and is_binary(next_node, "set")
            and node.left == next_node.right
        ):
            out = IrBinary(op="set", left=next_node.left, right=node.right)
            yield out
        else:
            nodes.push(next_node)
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


def rename_temp_scores(
    opt: Optimizer,
    nodes: Iterable[IrOperation],
) -> Iterable[IrOperation]:
    nodes = tuple(nodes)
    opt.temp_score.reset()

    source_map: dict[IrSource, IrSource] = {}

    def replace_source(node: IrNode) -> IrNode:
        if not isinstance(node, IrSource):
            return node

        if not node.temp:
            return node

        if node not in source_map:
            if isinstance(node, IrScore):
                source_map[node] = opt.generate_score()
            else:
                source_map[node] = node

        return source_map[node]

    for node in nodes:
        if not is_op(node):
            yield node
            continue

        store = tuple((type, replace_source(s)) for type, s in node.store)

        if is_unary(node):
            yield replace(node, target=replace_source(node.target), store=store)
        elif is_binary(node):
            yield replace(
                node,
                left=replace_source(node.left),
                right=replace_source(node.right),
                store=store,
            )
        else:
            yield replace(node, store=store)
