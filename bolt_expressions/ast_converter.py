from dataclasses import dataclass, field
from typing import Any, Generator, Iterable, cast
from mecha import AstChildren, AstCommand, Mecha, Visitor, rule, AstRoot
from nbtlib import Byte, Short, Int, Long, Float, Double  # type: ignore

from .typing import NBT_TYPE_STRING, NbtTypeString, NumericNbtValue
from .utils import insert_nested_commands, type_name

from .optimizer import (
    IrBinary,
    IrBinaryCondition,
    IrBoolScore,
    IrBranch,
    IrCast,
    IrCondition,
    IrData,
    IrInsert,
    IrLiteral,
    IrNode,
    IrRaw,
    IrScore,
    IrSet,
    IrSource,
    IrOperation,
    IrStore,
    IrChildren,
    IrUnary,
    IrUnaryCondition,
)

__all__ = [
    "InvalidOperand",
    "AstConverter",
]


class InvalidOperand(Exception):
    def __init__(self, op: str, *operands: Any):
        fmt = ", ".join(f"'{type_name(operand)}'" for operand in operands)
        super().__init__(f"Invalid operand(s) for '{op}' operation: {fmt}.")


@dataclass(kw_only=True)
class AstConverter(Visitor):
    default_nbt_type: NbtTypeString

    mc: Mecha
    result: list[AstCommand] = field(default_factory=list)

    def __call__(self, nodes: Iterable[IrOperation]) -> AstChildren[AstCommand]:  # type: ignore
        prev_result = self.result
        self.result = []

        for node in nodes:
            self.invoke(node)

        result = AstChildren(self.result)
        self.result = prev_result
        return result

    def add_result(
        self,
        cmd: str,
        store: IrChildren[IrStore] | None = None,
        children: AstChildren[AstCommand] | None = None,
    ) -> None:
        if store:
            prefix = tuple(self.invoke(s) for s in store)
            cmd = " ".join((*prefix, cmd))

        node = self.mc.parse(cmd, using="command")

        if children:
            node = insert_nested_commands(node, AstRoot(commands=children))

        self.result.append(node)

    @rule(IrNode)
    def fallback(self, node: IrNode):
        raise TypeError(f"Could not convert object '{node}' to AST.")

    @rule(IrRaw)
    def raw(self, node: IrRaw[AstCommand]):
        self.result.append(node.node)

    @rule(IrScore)
    def score(self, node: IrScore) -> str:
        return f"{node.holder} {node.obj}"

    @rule(IrData)
    def data(self, node: IrData) -> str:
        if not len(node.path):
            return f"{node.type} {node.target}"
        return f"{node.type} {node.target} {node.path}"

    @rule(IrLiteral)
    def literal(self, node: IrLiteral) -> str:
        return node.value.snbt()  # type: ignore

    @rule(IrStore)
    def store(self, node: IrStore) -> Generator[IrNode, str, str]:
        value = yield node.value
        type = node.type.value

        match node.value:
            case IrScore():
                return f"execute store {type} score {value} run"
            case IrData() as d:
                nbt_type = self.serialize_nbt_type(d.nbt_type)
                return f"execute store {type} {value} {nbt_type} 1 run"
            case _:
                raise ValueError(f"Invalid store source '{node.value}'.")

    @rule(IrBinaryCondition, op="less_than")
    def less_than(self, node: IrBinaryCondition) -> Generator[IrNode, str, str]:
        left = yield node.left
        right = yield node.right
        test = "unless" if node.negated else "if"

        match node.left, node.right:
            case IrScore(), IrScore():
                return f"execute {test} score {left} < {right}"
            case IrScore(), IrLiteral() as r:
                value = cast(NumericNbtValue, r.value)
                right = str(value - 1)
                return f"execute {test} score {left} matches ..{right}"
            case IrLiteral() as l, IrScore():
                value = cast(NumericNbtValue, l.value)
                right = str(value + 1)
                return f"execute {test} score {right} matches {left}.."
            case l, r:
                raise InvalidOperand(node.op, l, r)

    @rule(IrBinaryCondition, op="greater_than")
    def greater_than(self, node: IrBinaryCondition) -> Generator[IrNode, str, str]:
        left = yield node.left
        right = yield node.right
        test = "unless" if node.negated else "if"

        match node.left, node.right:
            case IrScore(), IrScore():
                return f"execute {test} score {left} > {right}"
            case IrScore(), IrLiteral() as r:
                value = cast(NumericNbtValue, r.value)
                right = str(value + 1)
                return f"execute {test} score {left} matches {right}.."
            case IrLiteral() as l, IrScore():
                value = cast(NumericNbtValue, l.value)
                right = str(value - 1)
                return f"execute {test} score {right} matches ..{left}"
            case l, r:
                raise InvalidOperand(node.op, l, r)

    @rule(IrBinaryCondition, op="greater_than_or_equal_to")
    def greater_than_or_qual_to(
        self, node: IrBinaryCondition
    ) -> Generator[IrNode, str, str]:
        left = yield node.left
        right = yield node.right
        test = "unless" if node.negated else "if"

        match node.left, node.right:
            case IrScore(), IrScore():
                return f"execute {test} score {left} >= {right}"
            case IrScore(), IrLiteral():
                return f"execute {test} score {left} matches {right}.."
            case IrLiteral(), IrScore():
                return f"execute {test} score {right} matches ..{left}"
            case l, r:
                raise InvalidOperand(node.op, l, r)

    @rule(IrBinaryCondition, op="less_than_or_equal_to")
    def less_than_or_qual_to(
        self, node: IrBinaryCondition
    ) -> Generator[IrNode, str, str]:
        left = yield node.left
        right = yield node.right
        test = "unless" if node.negated else "if"

        match node.left, node.right:
            case IrScore(), IrScore():
                return f"execute {test} score {left} <= {right}"
            case IrScore(), IrLiteral():
                return f"execute {test} score {left} matches ..{right}"
            case IrLiteral(), IrScore():
                return f"execute {test} score {right} matches {left}.."
            case l, r:
                raise InvalidOperand(node.op, l, r)

    @rule(IrBinaryCondition, op="equal")
    def equal(self, node: IrBinaryCondition) -> Generator[IrNode, str, str]:
        left = yield node.left
        right = yield node.right
        test = "unless" if node.negated else "if"

        match node.left, node.right:
            case IrScore(), IrScore():
                return f"execute {test} score {left} = {right}"
            case IrScore(), IrLiteral():
                return f"execute {test} score {left} matches {right}"
            case IrLiteral(), IrScore():
                return f"execute {test} score {right} matches {left}"
            case l, r:
                raise InvalidOperand(node.op, l, r)

    @rule(IrUnaryCondition, op="boolean")
    def boolean(self, node: IrUnaryCondition) -> Generator[IrNode, str, str]:
        target = yield node.target
        test = "unless" if node.negated else "if"

        match node.target:
            case IrBoolScore():
                return f"execute {test} score {target} matches 1"
            case IrScore() if node.negated:
                return f"execute unless score {target} matches ..-1 unless score {target} matches 1.."
            case IrScore() if not node.negated:
                return f"execute if score {target} matches -2147483648.. unless score {target} matches 0"
            case IrData():
                return f"execute {test} data {target}"
            case t:
                raise InvalidOperand(node.op, t)

    @rule(IrBranch)
    def branch(self, node: IrBranch) -> Generator[IrNode, str, None]:
        target = yield node.target

        match node.target:
            case IrSource() as source:
                cmd = yield IrUnaryCondition(op="boolean", target=source)
            case IrCondition():
                cmd = target

        children = self(node.children)
        self.add_result(cmd, node.store, children)

    @rule(IrBinary, op="add")
    def add(self, node: IrBinary) -> Generator[IrNode, str, None]:
        left = yield node.left
        right = yield node.right

        match node.left, node.right:
            case IrScore(), IrLiteral():
                cmd = f"scoreboard players add {left} {right}"
            case IrScore(), IrScore():
                cmd = f"scoreboard players operation {left} += {right}"
            case l, r:
                raise InvalidOperand(node.op, l, r)

        self.add_result(cmd, node.store)

    @rule(IrBinary, op="sub")
    def sub(self, node: IrBinary) -> Generator[IrNode, str, None]:
        left = yield node.left
        right = yield node.right

        match node.left, node.right:
            case IrScore(), IrLiteral():
                cmd = f"scoreboard players remove {left} {right}"
            case IrScore(), IrScore():
                cmd = f"scoreboard players operation {left} -= {right}"
            case l, r:
                raise InvalidOperand(node.op, l, r)

        self.add_result(cmd, node.store)

    @rule(IrBinary, op="mul")
    @rule(IrBinary, op="div")
    @rule(IrBinary, op="mod")
    @rule(IrBinary, op="min")
    @rule(IrBinary, op="max")
    def binary_score_only(self, node: IrBinary) -> Generator[IrNode, str, None]:
        left = yield node.left
        right = yield node.right

        operator = {
            "mul": "*=",
            "div": "/=",
            "mod": "%=",
            "min": "<",
            "max": ">",
        }
        match node.left, node.right:
            case IrScore(), IrScore():
                cmd = f"scoreboard players operation {left} {operator[node.op]} {right}"
            case l, r:
                raise InvalidOperand(node.op, l, r)

        self.add_result(cmd, node.store)

    @rule(IrBinary, op="append")
    def append(self, node: IrBinary) -> Generator[IrNode, str, None]:
        left = yield node.left
        right = yield node.right

        match node.left, node.right:
            case IrData(), IrLiteral():
                cmd = f"data modify {left} append value {right}"
            case IrData(), IrData():
                cmd = f"data modify {left} append from {right}"
            case l, r:
                raise InvalidOperand(node.op, l, r)

        self.add_result(cmd, node.store)

    @rule(IrBinary, op="prepend")
    def prepend(self, node: IrBinary) -> Generator[IrNode, str, None]:
        left = yield node.left
        right = yield node.right

        match node.left, node.right:
            case IrData(), IrLiteral():
                cmd = f"data modify {left} prepend value {right}"
            case IrData(), IrData():
                cmd = f"data modify {left} prepend from {right}"
            case l, r:
                raise InvalidOperand(node.op, l, r)

        self.add_result(cmd, node.store)

    @rule(IrInsert)
    def insert(self, node: IrInsert) -> Generator[IrNode, str, None]:
        left = yield node.left
        right = yield node.right
        index = node.index

        match node.left, node.right:
            case IrData(), IrLiteral():
                cmd = f"data modify {left} insert {index} value {right}"
            case IrData(), IrData():
                cmd = f"data modify {left} insert {index} from {right}"
            case l, r:
                raise InvalidOperand(node.op, l, r)

        self.add_result(cmd, node.store)

    @rule(IrBinary, op="merge")
    def merge(self, node: IrBinary) -> Generator[IrNode, str, None]:
        left = yield node.left
        right = yield node.right

        match node.left, node.right:
            case IrData() as l, IrLiteral() if not len(l.path):
                cmd = f"data merge {left} {right}"
            case IrData() as l, IrLiteral() if len(l.path):
                cmd = f"data modify {left} merge value {right}"
            case IrData() as l, IrData() if len(l.path):
                cmd = f"data modify {left} merge from {right}"
            case l, r:
                raise InvalidOperand(node.op, l, r)

        self.add_result(cmd, node.store)

    @rule(IrUnary, op="remove")
    def remove(self, node: IrUnary) -> Generator[IrNode, str, None]:
        target = yield node.target

        match node.target:
            case IrData():
                cmd = f"data remove {target}"
            case t:
                raise InvalidOperand(node.op, t)

        self.add_result(cmd, node.store)

    @rule(IrUnary, op="reset")
    def reset_op(self, node: IrUnary) -> Generator[IrNode, str, None]:
        target = yield node.target

        match node.target:
            case IrScore():
                cmd = f"scoreboard players reset {target}"
            case t:
                raise InvalidOperand(node.op, t)

        self.add_result(cmd, node.store)

    @rule(IrUnary, op="enable")
    def enable(self, node: IrUnary) -> Generator[IrNode, str, None]:
        target = yield node.target

        match node.target:
            case IrScore():
                cmd = f"scoreboard players enable {target}"
            case t:
                raise InvalidOperand(node.op, t)

        self.add_result(cmd, node.store)

    def serialize_nbt_type(self, value: Any) -> NbtTypeString:
        if isinstance(value, str) and value in NBT_TYPE_STRING:
            return value

        if not isinstance(value, type):
            return self.default_nbt_type

        if issubclass(value, Byte):
            return "byte"
        if issubclass(value, Short):
            return "short"
        if issubclass(value, Long):
            return "long"
        if issubclass(value, Double):
            return "double"
        if issubclass(value, Float):
            return "float"
        if issubclass(value, Int):
            return "int"

        return self.default_nbt_type

    def serialize_cast(self, data: IrData) -> tuple[str, str]:
        cast_type = data.nbt_type
        scale = data.scale if data.scale is not None else 1

        if not isinstance(cast_type, str):
            cast_type = self.serialize_nbt_type(cast_type)

        if cast_type is None:
            cast_type = self.default_nbt_type

        return (cast_type, str(scale))

    @rule(IrSet)
    def set(self, node: IrBinary) -> Generator[IrNode, str, None]:
        left = yield node.left
        right = yield node.right

        match node.left, node.right:
            case IrScore(), IrLiteral():
                cmd = f"scoreboard players set {left} {right}"
            case IrScore(), IrScore():
                cmd = f"scoreboard players operation {left} = {right}"
            case IrData(), IrLiteral():
                cmd = f"data modify {left} set value {right}"
            case IrData(), IrData():
                cmd = f"data modify {left} set from {right}"
            case IrScore(), IrCondition():
                cmd = f"execute store success score {left} run {right}"
            case IrData(), IrCondition():
                cmd = f"execute store success {left} byte 1 run {right}"
            case l, r:
                raise InvalidOperand(node.op, l, r)

        self.add_result(cmd, node.store)

    @rule(IrCast, op="cast")
    def cast(self, node: IrCast) -> Generator[IrNode, str, None]:
        left = yield node.left
        right = yield node.right

        nbt_type = self.serialize_nbt_type(node.cast_type)
        scale = node.scale

        match node.left, node.right:
            case IrData(), IrLiteral():
                cmd = f"data modify {left} set value {right}"
            case IrData() as l, IrData() as r:
                cmd = f"execute store result {left} {nbt_type} {scale} run data get {right} 1"
            case IrData() as l, IrScore():
                cmd = f"execute store result {left} {nbt_type} {scale} run scoreboard players get {right}"
            case IrData(), IrCondition():
                cmd = f"execute store success {left} {nbt_type} {scale} run {right}"
            case IrScore(), IrLiteral():
                cmd = f"scoreboard players set {left} {right}"
            case IrScore(), IrData() as r:
                cmd = f"execute store result score {left} run data get {right} {scale}"
            case IrScore(), IrCondition():
                cmd = f"execute store success score {left} run {right}"
            case l, r:
                raise InvalidOperand(node.op, l, r)

        self.add_result(cmd, node.store)
