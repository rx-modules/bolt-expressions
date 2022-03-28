from typing import TYPE_CHECKING, Dict, Iterable, List

if TYPE_CHECKING:
    from .operations import Operation

Command: type = str


def get_templates() -> Dict[str, str]:
    return {
        "set:literal": "scoreboard players set {former} {latter}",
        "add:literal": "scoreboard players add {former} {latter}",
        "subtract:literal": "scoreboard players remove {former} {latter}",
        "set:score": "scoreboard players operation {former} = {latter}",
        "add:score": "scoreboard players operation {former} += {latter}",
        "subtract:score": "scoreboard players operation {former} -= {latter}",
        "multiply:score": "scoreboard players operation {former} *= {latter}",
        "divide:score": "scoreboard players operation {former} /= {latter}",
        "modulus:score": "scoreboard players operation {former} %= {latter}",
        "greaterthan:score": "scoreboard players operation {former} > {latter}",
        "lessthan:score": "scoreboard players operation {former} < {latter}",
    }


def resolve(nodes: List["Operation"]) -> Iterable[Command]:
    """Transforms a list of operation nodes into command strings."""
    yield from map(generate_node, nodes)


def get_type(node: "Operation"):
    # optimizer might convert an int score back to a literal int
    # for operations like Set, Add and Subtract
    return "literal" if type(node.latter) is int else "score"


def generate_node(node: "Operation") -> Command:
    id = node.__class__.__name__.lower()  # TODO Operation should have an id property
    node_type = get_type(node)
    template = get_templates()[f"{id}:{node_type}"]
    return template.format(former=node.former, latter=node.latter)
