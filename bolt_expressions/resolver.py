from typing import Dict, Iterable, List

from .operations import GenericValue, Operation
from .sources import DataSource, ScoreSource

Command: type = str


def get_templates() -> Dict[str, str]:
    return {
        "set:score:literal": lambda op: f"scoreboard players set {op.former} {op.latter}",
        "add:score:literal": lambda op: f"scoreboard players add {op.former} {op.latter}",
        "subtract:score:literal": lambda op: f"scoreboard players remove {op.former} {op.latter}",
        "set:score:score": lambda op: f"scoreboard players operation {op.former} = {op.latter}",
        "add:score:score": lambda op: f"scoreboard players operation {op.former} += {op.latter}",
        "subtract:score:score": lambda op: f"scoreboard players operation {op.former} -= {op.latter}",
        "multiply:score:score": lambda op: f"scoreboard players operation {op.former} *= {op.latter}",
        "divide:score:score": lambda op: f"scoreboard players operation {op.former} /= {op.latter}",
        "modulus:score:score": lambda op: f"scoreboard players operation {op.former} %= {op.latter}",
        "min:score:score": lambda op: f"scoreboard players operation {op.former} < {op.latter}",
        "max:score:score": lambda op: f"scoreboard players operation {op.former} > {op.latter}",
        "set:data:literal": lambda op: f"data modify {op.former} set value {op.latter}",
        "set:data:data": lambda op: f"data modify {op.former} set from {op.latter}",
        "set:data:score": lambda op: f"execute store result {op.former} {op.former._number_type} {op.former._scale} run scoreboard players get {op.latter}",
        "set:score:data": lambda op: f"execute store result score {op.former} run data get {op.latter} {op.latter._scale}",
        "append:data:literal": lambda op: f"data modify {op.former} append value {op.latter}",
        "append:data:data": lambda op: f"data modify {op.former} append from {op.latter}",
        "prepend:data:literal": lambda op: f"data modify {op.former} prepend value {op.latter}",
        "prepend:data:data": lambda op: f"data modify {op.former} prepend from {op.latter}",
        "insert:data:literal": lambda op: f"data modify {op.former} insert {op.index} value {op.latter}",
        "insert:data:data": lambda op: f"data modify {op.former} insert {op.index} from {op.latter}",
        "merge:data:literal": lambda op: f"data modify {op.former} merge value {op.latter}",
        "merge:data:data": lambda op: f"data modify {op.former} merge from {op.latter}",
        "mergeroot:data:literal": lambda op: f"data merge {op.former} {op.latter}",
        "remove:data": lambda source: f"data remove {source}",
        "reset:score": lambda source: f"scoreboard players reset {source}",
        "enable:score": lambda source: f"scoreboard players enable {source}",
    }


def resolve(nodes: List[Operation]) -> Iterable[Command]:
    """Transforms a list of operation nodes into command strings."""
    yield from map(generate_node, nodes)


def get_type(node: GenericValue):
    # optimizer might convert an int score back to a literal int
    # for operations like Set, Add and Subtract
    if isinstance(node, ScoreSource):
        return "score"
    if isinstance(node, DataSource):
        return "data"
    return "literal"


def generate_node(node: Operation) -> Command:
    id = node.__class__.__name__.lower()  # TODO Operation should have an id property
    former_type = get_type(node.former)
    latter_type = get_type(node.latter)
    template_id = f"{id}:{former_type}:{latter_type}"
    return generate(template_id, node)


def generate(template_id: str, *args, **kwargs):
    template = get_templates()[template_id]
    if callable(template):
        return template(*args, *kwargs.values())
    return template.format(**kwargs)
