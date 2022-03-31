from typing import Dict, Iterable, List

from .operations import GenericValue, Operation
from .sources import DataSource, ScoreSource

Command: type = str


def get_templates() -> Dict[str, str]:
    return {
        "set:score:literal": "scoreboard players set {former} {latter}",
        "add:score:literal": "scoreboard players add {former} {latter}",
        "subtract:score:literal": "scoreboard players remove {former} {latter}",
        "set:score:score": "scoreboard players operation {former} = {latter}",
        "add:score:score": "scoreboard players operation {former} += {latter}",
        "subtract:score:score": "scoreboard players operation {former} -= {latter}",
        "multiply:score:score": "scoreboard players operation {former} *= {latter}",
        "divide:score:score": "scoreboard players operation {former} /= {latter}",
        "modulus:score:score": "scoreboard players operation {former} %= {latter}",
        "min:score:score": "scoreboard players operation {former} < {latter}",
        "max:score:score": "scoreboard players operation {former} > {latter}",
        "set:data:literal": "data modify {former} set value {latter}",
        "set:data:data": "data modify {former} set from {latter}",
        "set:data:score": lambda f, l: f"execute store result {f} {f._number_type} {f._scale} run scoreboard players get {l}",
        "set:score:data": lambda f, l: f"execute store result score {f} run data get {l} {l._scale}",
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
    template = get_templates()[f"{id}:{former_type}:{latter_type}"]
    if callable(template):
        return template(node.former, node.latter)
    return template.format(former=node.former, latter=node.latter)
