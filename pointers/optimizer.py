from typing import Any, Callable, Dict, Iterable, List, TYPE_CHECKING

from rich import print
from rich.pretty import pprint

from .sources import ConstantScoreSource, ScoreSource, TempScoreSource
from . import operations as op

if TYPE_CHECKING:
    Rule = Callable[[Iterable[op.Operation]], None]

class Optimizer:
    rules: List["Rule"] = []

    @classmethod
    def rule(cls, f):
        cls.rules.append(f)

    @classmethod
    def optimize(cls, nodes: Iterable["op.Operation"]):
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
    collapsed_last = False
    prev_node = next(nodes)
    for node in nodes:
        #print(f"\nPrevious node is {prev_node}")
        #print(f"Current nodes is {node}")
        if (
            type(prev_node) in (op.Add, op.Multiply)
            and type(node) is op.Set
            and prev_node.former == node.latter
            and prev_node.latter == node.former
        ):
            #print("Commutative set collapsing matched!")
            yield prev_node.__class__(
                node.former, node.latter
            )
            collapsed_last = True
        else:
            yield prev_node
            collapsed_last = False
        prev_node = node
    # If not collapsed in the last loop: yield last node
    if not collapsed_last: yield prev_node

@Optimizer.rule
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

@Optimizer.rule
def set_to_self_removal(nodes: Iterable["op.Operation"]):
    """ Removes Set operations that have the same former and latter source"""
    for node in nodes:
        if type(node) is op.Set:
            if node.former != node.latter: yield node
        else:
            yield node
            

@Optimizer.rule
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
def print_empty(nodes: Iterable["op.Operation"]) -> Iterable["op.Operation"]:
    for node in nodes:
        # print()
        yield node
