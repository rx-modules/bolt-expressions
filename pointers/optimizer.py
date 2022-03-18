from typing import Any, Callable, Dict, Generator, Iterable, List, TYPE_CHECKING, TypeVar, Union

from rich import print
from rich.pretty import pprint

from itertools import chain
from functools import wraps

from .sources import ConstantScoreSource, ScoreSource, TempScoreSource
from . import operations as op

if TYPE_CHECKING:
    Rule = Callable[[Iterable[op.Operation]], None]

T = TypeVar("T")

DefaultValue = object()

class SmartGenerator(Generator):
    def __init__(self, gen):
        self._gen: Generator[T] = gen

    def __iter__(self):
        self._pre: List[T] = []
        return self
    
    def __next__(self) -> T:
        if self._pre:
            return self._pre.pop()
        
        return next(self._values)  # raises StopIteration for us
    
    def __call__(self, values) -> Iterable[T]:
        self._values: Iterable[T] = self._gen(values)
        return self
    
    def push(self, val: T):
        self._pre.append(val)
    
    def send(self, val: T):
        return self._gen.send(val)
    
    def throw(self, val: T):
        raise self._gen.throw(val)


class Optimizer:
    rules: List["Rule"] = []

    @classmethod
    def rule(cls, f: Iterable["op.Operation"]):
        cls.rules.append(SmartGenerator(f))

    @classmethod
    def optimize(cls, nodes: Iterable["op.Operation"]):
        nodes = (node for node in nodes) # temp

        for rule in cls.rules:
            nodes = rule(nodes)

        yield from nodes

@Optimizer.rule
def temp_var_collapsing(nodes: Iterable["op.Operation"]):
    map: Dict[TempScoreSource, TempScoreSource] = {}

    def get_replaced(source):
        # get the very last source if they're chained
        replaced = map.get(source)
        return get_replaced(replaced) if replaced else source

    for node in nodes:
        # print("[bold]temp_var_collapsing[/bold]", node)
        if (
            type(node) is op.Set
            and type(node.former) is TempScoreSource
            and type(node.latter) is TempScoreSource
        ):
            # peek: Operation = next(nodes)  # deletes current node
            replaced_latter = get_replaced(node.latter)
            map[node.former] = replaced_latter
            # yield peek.__class__(node.latter, peek.latter)
        else:
            yield node.__class__(get_replaced(node.former), get_replaced(node.latter))

#@Optimizer.rule
def noncommutative_set_collapsing(nodes: Iterable["op.Operation"]):
    """
        For noncommutative operations:

        scoreboard players operation $i1 temp = @s rx.uid
        scoreboard players operation $i1 temp -= $i0 temp
        scoreboard players operation @s rx.uid = $i1 temp

        Becomes:

        scoreboard players operation @s rx.uid -= $i0 temp

    """
    ...

@Optimizer.rule
def commutative_set_collapsing(nodes: Iterable["op.Operation"]):
    """
        For commutative operations:

        scoreboard players operation $i1 temp += $i0 temp
        scoreboard players operation $i0 temp = $i1 temp

        Becomes:

        scoreboard players operation $i0 temp += $i1 temp
    """
    for node in nodes:
        next_node: Union["op.Operation", None] = next(nodes, None)
        print("node", node)
        print("next_node", next_node)

        if (
            type(node) in (op.Add, op.Multiply)
            and type(next_node) is op.Set
            and node.former == next_node.latter
            and node.latter == next_node.former
        ):
            out = node.__class__(
                next_node.former, next_node.latter
            )
            print("new", out)
            yield out
        else:
            print("old", node)
            nodes.push(next_node)
            yield node

# @Optimizer.rule
def set_to_self_removal(nodes: Iterable["op.Operation"]):
    """ Removes Set operations that have the same former and latter source"""
    for node in nodes:
        if type(node) is op.Set:
            if node.former != node.latter: yield node
        else:
            yield node
            

# Optimizer.rule
def constant_to_literal_replacement(nodes: Iterable["op.Operation"]) -> Iterable["op.Operation"]:
    for node in nodes:
        # print("[bold]constant_to_literal_replacement[/bold]", node)
        if (
            isinstance(node, (op.Set, op.Add, op.Subtract))
            and type(node.latter) is ConstantScoreSource
        ):
            literal = node.latter.scoreholder[1:]
            yield node.__class__(node.former, int(literal))
        else:
            yield node


@Optimizer.rule
def print_node(nodes: Iterable["op.Operation"]) -> Iterable["op.Operation"]:
    for node in nodes:
        print("end", node)
        print()
        yield node

# @Optimizer.rule
def output_score_replacement(nodes: Iterable["op.Operation"]):
    """
        Replace the outermost temp score by the output score.
        If expression tree uses the output score, this rule
        won't be applied.
    """
    all_nodes = list(nodes)
    #print("[bold]Applying output score replacement on tree:[/bold]")
    #pprint(all_nodes)
    last_node = all_nodes[-1]
    target_var = last_node.latter
    output_var = last_node.former
    can_replace = False
    #print(f"Last node is {last_node}")
    if len(all_nodes) > 1 and type(last_node) is op.Set:
        for node in all_nodes[1:]: # Ignore the first Set operation
            #print(f"Is {node.latter} equal to {output_var}? {node.latter == output_var}")
            if node.latter == output_var: break
        else: can_replace = True
    #print(f"Can replace output score? {can_replace}")
    def replace(source):
        if source == target_var: return output_var
        return source
    if can_replace:
        for node in all_nodes:
            yield node.__class__(
                replace(node.former),
                replace(node.latter)
            )
    else: yield from all_nodes
