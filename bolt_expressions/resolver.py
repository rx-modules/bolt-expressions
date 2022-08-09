from typing import Dict, Iterable, List


from .node import ExpressionNode
from .operations import GenericValue, Operation, UnaryOperation, BinaryOperation
from .sources import DataSource, ScoreSource, Source

Command: type = str


def get_templates() -> Dict[str, str]:
    return {
        "node": resolve_operation,
        "operation:unary": resolve_unary,
        "operation:binary": resolve_binary,
        "execute": resolve_execute,
        "execute:store": resolve_execute_store,
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
        "set:data:data": resolve_set_data_data,
        "set:data:score": lambda op: f"execute store result {op.former} {op.former.get_type()} {op.former._scale} run scoreboard players get {op.latter}",
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
        # CONDITIONS
        "istrue": lambda node: generate(f"istrue:{get_type(node)}", node),
        "istrue:score": lambda source: f"execute if score {source} matches -2147483648.. unless score {source} matches 0",
        "istrue:data": lambda source: f"execute if data {source}",
        "not:score": lambda op: f"execute unless score {op.value} matches ..-1 unless score {op.value} matches 1..",
        "not:data": lambda op: f"execute unless data {op.value}",
        "lessthan:score:score": lambda op: f"execute if score {op.former} < {op.latter}",
        "greaterthan:score:score": lambda op: f"execute if score {op.former} > {op.latter}",
        "lessthanorequalto:score:score": lambda op: f"execute if score {op.former} <= {op.latter}",
        "lessthanorequalto:score:literal": lambda op: f"execute if score {op.former} matches ..{op.latter}",
        "greaterthanorequalto:score:score": lambda op: f"execute if score {op.former} >= {op.latter}",
        "greaterthanorequalto:score:literal": lambda op: f"execute if score {op.former} matches {op.latter}..",
    }


def get_type(node: GenericValue):
    # optimizer might convert an int score back to a literal int
    # for operations like Set, Add and Subtract
    if isinstance(node, ScoreSource):
        return "score"
    if isinstance(node, DataSource):
        return "data"
    return "literal"


def generate(template_id: str, *args, **kwargs):
    template = get_templates()[template_id]
    return template(*args, *kwargs.values())


def resolve_execute(node: Operation):
    args = []
    for source, type in node.store:
        args.append(generate("execute:store", source, type))
    return " ".join(("execute", *args, "run ")) if args else ""


def resolve_execute_store(source: Source, type: str):
    if isinstance(source, ScoreSource):
        return f"store {type} score {source}"
    if isinstance(source, DataSource):
        return f"store {type} {source} {source.get_type()} {source._scale}"


def resolve_set_data_data(op: Operation):
    if (
        op.former._scale != 1
        or op.latter._scale != 1
        or op.former._nbt_type is not None
    ):
        return f"execute store result {op.former} {op.former.get_type()} {op.former._scale} run data get {op.latter} {op.latter._scale}"
    return f"data modify {op.former} set from {op.latter}"


def resolve_binary(node: BinaryOperation):
    id = node.__class__.__name__.lower()  # TODO Operation should have an id property
    former_type = get_type(node.former)
    latter_type = get_type(node.latter)
    template_id = f"{id}:{former_type}:{latter_type}"
    cmd = generate("execute", node)
    return cmd + generate(template_id, node)

def resolve_unary(node: UnaryOperation):
    id = node.__class__.__name__.lower()
    value_type = get_type(node.value)
    template_id = f"{id}:{value_type}"
    cmd = generate("execute", node)
    return cmd + generate(template_id, node)

def resolve_operation(node: Operation):
    if isinstance(node, UnaryOperation):
        return generate("operation:unary", node)
    if isinstance(node, BinaryOperation):
        return generate("operation:binary", node)
    

def resolve(nodes: List[Operation]) -> Iterable[Command]:
    """Transforms a list of operation nodes into command strings."""
    yield from map(resolve_operation, nodes)
