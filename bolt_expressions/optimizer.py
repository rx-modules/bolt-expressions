from dataclasses import dataclass, field, replace
from fractions import Fraction
from functools import cached_property
from types import TracebackType
from typing import (
    Any,
    Callable,
    Generator,
    Iterable,
    Iterator,
    List,
    Protocol,
    Type,
    TypeVar,
    Union,
    cast,
)

from beet import Context
from nbtlib import Double, Float, Int, Numeric
from rich import print
from rich.pretty import pprint

from .exceptions import TypeCheckError, get_exception_chain
from .literals import Literal
from .log import BoltLogger
from .operations import (
    Add,
    DataOperation,
    Divide,
    Max,
    Min,
    Modulus,
    Multiply,
    Operation,
    ScoreOperation,
    Set,
    Subtract,
)
from .sources import ConstantScoreSource, DataSource, ScoreSource, Source
from .typing import (
    DataNode,
    DataType,
    cast_value,
    check_type,
    format_type,
    get_optional_type,
    infer_type,
    is_numeric,
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
    "output_score_replacement",
    "multiply_divide_by_one_removal",
    "add_subtract_by_zero_removal",
    "set_to_self_removal",
    "set_and_get_cleanup",
    "literal_to_constant_replacement",
]

T = TypeVar("T")


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
    _pre: List[T]

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

    def send(self, val: None, /) -> T:
        ...

    def throw(
        self,
        typ: Type[BaseException],
        val: BaseException | object = ...,
        tb: TracebackType | None = ...,
        /,
    ) -> T:
        ...


Rule = Callable[[Iterable[T]], Iterable[T]]

SmartRule = Callable[[SmartGenerator[T]], Iterable[T]]


def use_smart_generator(func: SmartRule[T]) -> Rule[T]:
    """
    Provides a `SmartGenerator` object as first argument to the decorated rule.
    Returned function still takes an `Iterable` object.
    """

    def rule(arg: Iterable[T]) -> Iterable[T]:
        return func(SmartGenerator(arg))

    return rule


def smart_generator(func: Rule[T]) -> Callable[[Iterable[T]], SmartGenerator[T]]:
    def rule(arg: Iterable[T]):
        return SmartGenerator(func(arg))

    return rule


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

    rules: List[Rule[Operation]] = field(default_factory=list)

    def add_rules(self, *funcs: Rule[Operation], index: int | None = None):
        """Registers new rules, also converts the decorated generator into a `SmartGenerator`"""

        if index is None:
            index = len(self.rules)

        index = min(len(self.rules), index)

        for f in funcs[::-1]:
            self.rules.insert(index, f)

    def optimize(self, nodes: Iterable[Operation]):
        """Performs the optimization by sending all nodes through the rules."""

        for rule in self.rules:
            nodes = rule(nodes)

        yield from nodes

    __call__ = optimize


@dataclass
class TypeChecker:
    ctx: Context

    @cached_property
    def log(self) -> BoltLogger:
        return self.ctx.inject(BoltLogger)

    @staticmethod
    def get_type(value: Any) -> DataType:
        if type := getattr(value, "readtype", None):
            return type

        if isinstance(value, Literal):
            value = value.value

        return infer_type(value)

    def __call__(self, nodes: Iterable[Operation]) -> Iterable[Operation]:
        nodes = self.cast(nodes)
        nodes = self.check(nodes)

        yield from nodes

    def cast(self, nodes: Iterable[Operation]) -> Iterable[Operation]:
        for node in nodes:
            if isinstance(node, Set) and isinstance(node.former, DataSource):
                former, latter, cast_type = node.former, node.latter, node.cast

                changed = False

                write = former.writetype
                read = self.get_type(latter)

                if opt_write := get_optional_type(write):
                    write = opt_write

                if isinstance(latter, Literal):
                    if value := cast_value(write, latter.value):
                        latter = replace(latter, value=value)
                        changed = True
                elif is_numeric(write) and write != read:
                    cast_type = write
                    changed = True

                if changed:
                    node = replace(node, cast=cast_type, latter=latter)

            yield node

    def check(self, nodes: Iterable[Operation]) -> Iterable[Operation]:
        for node in nodes:
            if isinstance(node, Set) and isinstance(node.former, DataSource):
                node = self.set(node)

            yield node

    def set(self, node: Set):
        former, latter = cast(DataSource, node.former), node.latter

        write = former.writetype
        read = self.get_type(latter)

        result_type = write
        result_children = {}

        match = None
        errors = ()
        flags = {"numeric_match": isinstance(latter, Literal)}

        try:
            match = check_type(write, read, **flags)
        except TypeCheckError as exc:
            errors = get_exception_chain(exc)

        if not match:
            if isinstance(latter, DataSource):
                msg = f"data source '{latter}' with read type '{format_type(read)}'"
            elif isinstance(latter, ScoreSource):
                msg = f"score '{latter}'"
            else:
                msg = f"value of type '{format_type(read)}'"

            self.log(
                "warn",
                f"Data source '{former}' with write type '{format_type(write)}' "
                + f"cannot be assigned to {msg}. "
                + " ".join(str(err) for err in errors),
            )

        if write is Any or (not match and not node.cast):
            result_type = read

        if isinstance(latter, DataSource):
            latter_node = latter._namespace.get_or_create(latter._path)  # type: ignore
            result_children = latter_node.children

        data_node = former._namespace.get_or_create(former._path)  # type: ignore

        data_node.set_type(result_type)
        data_node.set_children(result_children)

        return node


@use_smart_generator
def noncommutative_set_collapsing(nodes: SmartGenerator[Operation]):
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
            isinstance(node, Set)
            and isinstance(next_node, ScoreOperation)
            and isinstance(further_node, Set)
            and isinstance(further_node.former, ScoreSource)
            and node.latter == further_node.former
            and node.former == next_node.former
            and node.former == further_node.latter
        ):
            yield replace(
                next_node, former=further_node.former, latter=next_node.latter
            )
        else:
            nodes.push(further_node)
            nodes.push(next_node)
            yield node


@use_smart_generator
def commutative_set_collapsing(nodes: SmartGenerator[Operation]):
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
        next_node: Union[Operation, None] = next(nodes, None)
        # print("node", node)
        # print("next_node", next_node)

        if (
            isinstance(node, (Add, Multiply))
            and isinstance(next_node, Set)
            and isinstance(next_node.former, ScoreSource)
            and node.former == next_node.latter
            and node.latter == next_node.former
        ):
            yield replace(node, former=next_node.former, latter=next_node.latter)
        else:
            # print("old", node)
            nodes.push(next_node)
            yield node


@use_smart_generator
def data_set_scaling(nodes: SmartGenerator[Operation]):
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
        if isinstance(next_node, DataOperation):
            operation_node = next_node
            next_node = next(nodes, None)
        if (
            isinstance(node, (Multiply, Divide))
            and isinstance(next_node, Set)
            and isinstance(node.latter, Literal)
            and isinstance(next_node.former, DataSource)
            and node.former == next_node.latter
        ):
            scale = float(node.latter.value)

            if scale.is_integer():
                scale = int(scale)

            source = next_node.former
            number_type = source.writetype

            if isinstance(node, Divide):
                scale = 1 / scale

                if number_type is Any:
                    number_type = source._default_floating_point_type

            new_source = replace(source, _scale=scale, writetype=number_type)
            out = Set(new_source, node.former)

            if operation_node:
                yield operation_node  # yield the data operation node back in

            yield out
        else:
            nodes.push(next_node)
            nodes.push(operation_node)
            yield node


@use_smart_generator
def data_get_scaling(nodes: SmartGenerator[Operation]):
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
            isinstance(node, Set)
            and isinstance(next_node, (Multiply, Divide))
            and isinstance(node.latter, DataSource)
            and isinstance(next_node.latter, Literal)
            and node.former == next_node.former
        ):
            scale = float(next_node.latter.value)

            if scale.is_integer():
                scale = int(scale)

            if isinstance(next_node, Divide):
                scale = 1 / scale

            yield Set(node.former, replace(node.latter, _scale=scale))
        else:
            nodes.push(next_node)
            yield node


def multiply_divide_by_fraction(nodes: Iterable[Operation]):
    for node in nodes:
        if (
            isinstance(node, (Multiply, Divide))
            and isinstance(node.latter, Literal)
            and isinstance(node.latter.value, (Float, Double))
        ):
            value = Fraction(node.latter.value).limit_denominator()

            if isinstance(node, Divide):
                value = 1 / value

            yield Multiply.create(node.former, value.numerator)
            yield Divide.create(node.former, value.denominator)
        else:
            yield node


def output_score_replacement(nodes: Iterable[Operation]):
    """Replace the outermost temp score by the output score.
    If expression tree uses the output score, this rule won't be applied.
    """
    all_nodes = list(nodes)

    if all_nodes:
        # print("[bold]Applying output score replacement on tree:[/bold]")
        # pprint(all_nodes)
        last_node = all_nodes[-1]
        target_var = last_node.latter
        output_var = last_node.former
        can_replace = False
        # print(f"Last node is {last_node}")
        if (
            isinstance(output_var, ScoreSource)
            and isinstance(last_node, Set)
            and len(all_nodes) > 1
        ):
            for node in all_nodes[1:]:  # Ignore the first Set operation
                # print(f"Is {node.latter} equal to {output_var}? {node.latter == output_var}")
                if node.latter == output_var:
                    break
            else:
                can_replace = True
        # print(f"Can replace output score? {can_replace}")
        def replace_source(source: Source):
            if source == target_var:
                return output_var
            return source

        if can_replace:
            for node in all_nodes:
                yield replace(
                    node,
                    former=replace_source(node.former),
                    latter=replace_source(node.latter),
                )
        else:
            yield from all_nodes


def multiply_divide_by_one_removal(nodes: Iterable[Operation]):
    for node in nodes:
        if not (
            isinstance(node, (Multiply, Divide))
            and isinstance(node.latter, Literal)
            and node.latter.value == 1
        ):
            yield node


def add_subtract_by_zero_removal(nodes: Iterable[Operation]):
    for node in nodes:
        if not (
            isinstance(node, (Add, Subtract))
            and isinstance(node.latter, Literal)
            and node.latter.value == 0
        ):
            yield node


def set_to_self_removal(nodes: Iterable[Operation]):
    """Removes Set operations that have the same former and latter source.
    Should run after "output_score_replacement" is applied to clean up
    all the reduntant Sets created by the previous rule.
    """
    for node in nodes:
        if isinstance(node, Set):
            if node.former != node.latter:
                yield node
        else:
            yield node


@use_smart_generator
def set_and_get_cleanup(nodes: SmartGenerator[Operation]):
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
            isinstance(node, Set)
            and isinstance(next_node, Set)
            and node.former == next_node.latter
        ):
            out = Set(next_node.former, node.latter)
            yield out
        else:
            nodes.push(next_node)
            yield node


def literal_to_constant_replacement(
    nodes: Iterable[Operation],
):
    for node in nodes:
        if (
            isinstance(node, (Multiply, Divide, Min, Max, Modulus))
            and isinstance(node.latter, Literal)
            and isinstance(node.latter.value, Numeric)
        ):
            value = int(node.latter.value)
            constant = ConstantScoreSource.create(value)

            yield replace(node, former=node.former, latter=constant)
        else:
            yield node
