from fractions import Fraction
from functools import wraps
from itertools import chain
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Dict,
    Generator,
    Iterable,
    List,
    Optional,
    TypeVar,
    Union,
)

from nbtlib import Double, Float, Numeric

from . import operations as op
from .literals import Literal
from .sources import ConstantScoreSource, DataSource, ScoreSource, TempScoreSource

# from rich import print
# from rich.pretty import pprint

__all__ = [
    "SmartGenerator",
    "Optimizer",
    "dummy",
    "noncommutative_set_collapsing",
    "commutative_set_collapsing",
    "data_set_scaling",
    "data_get_scaling",
    "literal_to_constant_replacement",
    "output_score_replacement",
    "set_to_self_removal",
    "set_and_get_cleanup",
]

if TYPE_CHECKING:
    Rule = Callable[[Iterable[op.Operation]], None]

T = TypeVar("T")


class SmartGenerator(Generator):
    """Implements `.push(val)` which allows you to 'prepend' values to a generator.
    Allows you to peek values in the future, and return them to be consumed later.

    >>> gen = SmartGenerator(i for i in range(10))
    >>> val = next(gen)
    >>> gen.push(val)
    >>> next(gen)
    0
    """

    def __init__(self, func):
        self._func: Callable[..., Generator] = func

    def __iter__(self):
        self._pre: List[T] = []
        return self

    def __next__(self) -> T:
        if self._pre:
            return self._pre.pop()

        return next(self._values)  # raises StopIteration for us

    def __call__(self, values) -> Iterable[T]:
        self._values: Iterable[T] = self._func(values)
        return self

    def push(self, val: T):
        if val != None:
            self._pre.append(val)

    def send(self, val: T):
        return self._values.send(val)

    def throw(self, val: T):
        raise self._values.throw(val)


class Optimizer:
    """Handles the operation of various optimization rules.

    The `Optimizer.rule` decorates generator functions which process Operation nodes. Each rule
    must take and return a generator of Operation nodes. This usually involves a loop which
    steps through the generator and performs optimizations across the nodes.

    Each rule is converted into a `SmartGenerator`, which adds a `.push(value)` method allowing
    you to "peek" ahead by consuming value and prepending it back to the generator. Note, calling
    `next` manually in the loop will essentially consume the node, deleting it from the final output.

    The optimizer runs the nodes through the rules like a conveyor belt and each rule acts as a worker.
    The rules can perform transformations, take nodes off and add different ones on, or even collect
    all nodes, and put on a completely different set of nodes. This metaphor should be considered when
    writing new rules.
    """

    rules: List["Rule"] = []

    @classmethod
    def rule(cls, f: Iterable["op.Operation"]):
        """Registers new rules, also converts the decorated generator into a `SmartGenerator`"""
        cls.rules.append(SmartGenerator(f))

    @classmethod
    def optimize(cls, nodes: Iterable["op.Operation"]):
        """Performs the optimization by sending all nodes through the rules."""
        for rule in cls.rules:
            nodes = rule(nodes)

        yield from nodes


@Optimizer.rule
def dummy(nodes: Iterable["op.Operation"]):
    yield from nodes


@Optimizer.rule
def noncommutative_set_collapsing(nodes: Iterable["op.Operation"]):
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
            type(node) is op.Set
            and isinstance(next_node, op.ScoreOperation)
            and type(further_node) is op.Set
            and isinstance(further_node.former, ScoreSource)
            and node.latter == further_node.former
            and node.former == next_node.former
            and node.former == further_node.latter
        ):
            out = next_node.__class__(further_node.former, next_node.latter)
            yield out
        else:
            nodes.push(further_node)
            nodes.push(next_node)
            yield node


@Optimizer.rule
def commutative_set_collapsing(nodes: Iterable["op.Operation"]):
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
        next_node: Union["op.Operation", None] = next(nodes, None)
        # print("node", node)
        # print("next_node", next_node)

        if (
            type(node) in (op.Add, op.Multiply)
            and type(next_node) is op.Set
            and isinstance(next_node.former, ScoreSource)
            and node.former == next_node.latter
            and node.latter == next_node.former
        ):
            out = node.__class__(next_node.former, next_node.latter)
            # print("new", out)
            yield out
        else:
            # print("old", node)
            nodes.push(next_node)
            yield node


@Optimizer.rule
def data_set_scaling(nodes: Iterable["op.Operation"]):
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
        if isinstance(next_node, op.DataOperation):
            operation_node = next_node
            next_node = next(nodes, None)
        if (
            isinstance(node, (op.Multiply, op.Divide))
            and isinstance(next_node, op.Set)
            and isinstance(node.latter, Literal)
            and isinstance(next_node.former, DataSource)
            and node.former == next_node.latter
        ):
            scale = float(node.latter.value)

            if scale.is_integer():
                scale = int(scale)

            source = next_node.former
            number_type = source._nbt_type

            if isinstance(node, op.Divide):
                scale = 1 / scale
                number_type = number_type or source._default_floating_point_type

            new_source = source._copy(scale=scale, nbt_type=number_type)
            out = op.Set(new_source, node.former)

            if operation_node:
                yield operation_node  # yield the data operation node back in

            yield out
        else:
            nodes.push(next_node)
            nodes.push(operation_node)
            yield node


@Optimizer.rule
def data_get_scaling(nodes: Iterable["op.Operation"]):
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
            isinstance(node, op.Set)
            and isinstance(next_node, (op.Multiply, op.Divide))
            and isinstance(node.latter, DataSource)
            and isinstance(next_node.latter, Literal)
            and node.former == next_node.former
        ):
            scale = float(next_node.latter.value)

            if scale.is_integer():
                scale = int(scale)

            if isinstance(next_node, op.Divide):
                scale = 1 / scale

            yield op.Set(node.former, node.latter._copy(scale=scale))
        else:
            nodes.push(next_node)
            yield node


@Optimizer.rule
def multiply_divide_by_fraction(nodes: Iterable["op.Operation"]):
    for node in nodes:
        if (
            isinstance(node, (op.Multiply, op.Divide))
            and isinstance(node.latter, Literal)
            and isinstance(node.latter.value, (Float, Double))
        ):
            value = Fraction(node.latter.value).limit_denominator()

            if isinstance(node, op.Divide):
                value = 1 / value

            yield op.Multiply.create(node.former, value.numerator)
            yield op.Divide.create(node.former, value.denominator)
        else:
            yield node


@Optimizer.rule
def output_score_replacement(nodes: Iterable["op.Operation"]):
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
            and type(last_node) is op.Set
            and len(all_nodes) > 1
        ):
            for node in all_nodes[1:]:  # Ignore the first Set operation
                # print(f"Is {node.latter} equal to {output_var}? {node.latter == output_var}")
                if node.latter == output_var:
                    break
            else:
                can_replace = True
        # print(f"Can replace output score? {can_replace}")
        def replace(source):
            if source == target_var:
                return output_var
            return source

        if can_replace:
            for node in all_nodes:
                yield node.__class__(replace(node.former), replace(node.latter))
        else:
            yield from all_nodes


@Optimizer.rule
def multiply_divide_by_one_removal(nodes: Iterable["op.Operation"]):
    for node in nodes:
        if not (
            isinstance(node, (op.Multiply, op.Divide))
            and isinstance(node.latter, Literal)
            and node.latter.value == 1
        ):
            yield node


@Optimizer.rule
def add_subtract_by_zero_removal(nodes: Iterable["op.Operation"]):
    for node in nodes:
        if not (
            isinstance(node, (op.Add, op.Subtract))
            and isinstance(node.latter, Literal)
            and node.latter.value == 0
        ):
            yield node


@Optimizer.rule
def set_to_self_removal(nodes: Iterable["op.Operation"]):
    """Removes Set operations that have the same former and latter source.
    Should run after "output_score_replacement" is applied to clean up
    all the reduntant Sets created by the previous rule.
    """
    for node in nodes:
        if type(node) is op.Set:
            if node.former != node.latter:
                yield node
        else:
            yield node


@Optimizer.rule
def set_and_get_cleanup(nodes: Iterable["op.Operation"]):
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
            isinstance(node, op.Set)
            and isinstance(next_node, op.Set)
            and node.former == next_node.latter
        ):
            out = op.Set(next_node.former, node.latter)
            yield out
        else:
            nodes.push(next_node)
            yield node


@Optimizer.rule
def literal_to_constant_replacement(
    nodes: Iterable["op.Operation"],
) -> Iterable["op.Operation"]:
    for node in nodes:
        if (
            isinstance(node, (op.Multiply, op.Divide, op.Min, op.Max, op.Modulus))
            and isinstance(node.latter, Literal)
            and isinstance(node.latter.value, Numeric)
        ):
            value = int(node.latter.value)
            constant = ConstantScoreSource.create(value)

            yield type(node).create(node.former, constant)
        else:
            yield node
