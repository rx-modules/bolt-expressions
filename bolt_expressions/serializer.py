from dataclasses import dataclass
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
    IrScore,
    IrSet,
    IrSource,
    IrUnary,
    IrUnaryCondition,
)

__all__ = [
    "InvalidOperand",
    "IrSerializer",
]


class InvalidOperand(Exception):
    def __init__(self, op: str, *operands: Any):
        fmt = ", ".join(f"'{type_name(operand)}'" for operand in operands)
        super().__init__(f"Invalid operand(s) for '{op}' operation: {fmt}.")


@dataclass(frozen=True)
class Command:
    value: str

    def to_ast(self, mc: Mecha) -> AstCommand:
        return mc.parse(self.value, using="command")
    
    def __str__(self) -> str:
        return self.value

@dataclass(frozen=True)
class BranchCommand(Command):
    children: AstChildren[AstCommand] 

    def to_ast(self, mc: Mecha) -> AstCommand:
        command = super().to_ast(mc)
        root = AstRoot(commands=self.children)
        return insert_nested_commands(command, root)


@dataclass(kw_only=True)
class IrSerializer(Visitor):
    default_nbt_type: NbtTypeString

    def __call__(self, nodes: Iterable[IrNode]) -> list[Command]:  # type: ignore
        result: list[Any] = []

        for node in nodes:
            self.invoke(node, result)

        return [
            Command(value) if not isinstance(value, Command) else value
            for value in result
        ]
    
    @rule(IrNode)
    def fallback(self, node: IrNode, _: list[Any]):
        raise TypeError(f"Could not serialize object '{node}'.")

    @rule(IrScore)
    def score(self, node: IrScore, _: list[str]) -> str:
        return f"{node.holder} {node.obj}"

    @rule(IrData)
    def data(self, node: IrData, _: list[str]) -> str:
        if not len(node.path):
            return f"{node.type} {node.target}"
        return f"{node.type} {node.target} {node.path}"

    @rule(IrLiteral)
    def literal(self, node: IrLiteral, _: list[str]) -> str:
        return node.value.snbt()  # type: ignore
    

    @rule(IrBinaryCondition, op="less_than")
    def less_than(self, node: IrBinaryCondition, _: list[str]) -> Generator[IrNode, str, str]:
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
    def greater_than(self, node: IrBinaryCondition, _: list[str]) -> Generator[IrNode, str, str]:
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
    def greater_than_or_qual_to(self, node: IrBinaryCondition, _: list[str]) -> Generator[IrNode, str, str]:
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
    def less_than_or_qual_to(self, node: IrBinaryCondition, _: list[str]) -> Generator[IrNode, str, str]:
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
    def equal(self, node: IrBinaryCondition, _: list[str]) -> Generator[IrNode, str, str]:
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
    def boolean(self, node: IrUnaryCondition, _: list[str]) -> Generator[IrNode, str, str]:
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
    def branch(self, node: IrBranch, result: list[Any]) -> Generator[IrNode, str, None]:
        target = yield node.target

        match node.target:
            case IrSource() as source:
                cmd = yield IrUnaryCondition(op="boolean", target=source)
            case IrCondition():
                cmd = target
        
        result.append(BranchCommand(cmd, node.children))

    @rule(IrBinary, op="add")
    def add(self, node: IrBinary, result: list[str]) -> Generator[IrNode, str, None]:
        left = yield node.left
        right = yield node.right

        match node.left, node.right:
            case IrScore(), IrLiteral():
                cmd = f"scoreboard players add {left} {right}"
            case IrScore(), IrScore():
                cmd = f"scoreboard players operation {left} += {right}"
            case l, r:
                raise InvalidOperand(node.op, l, r)

        result.append(cmd)

    @rule(IrBinary, op="sub")
    def sub(self, node: IrBinary, result: list[str]) -> Generator[IrNode, str, None]:
        left = yield node.left
        right = yield node.right

        match node.left, node.right:
            case IrScore(), IrLiteral():
                cmd = f"scoreboard players remove {left} {right}"
            case IrScore(), IrScore():
                cmd = f"scoreboard players operation {left} -= {right}"
            case l, r:
                raise InvalidOperand(node.op, l, r)

        result.append(cmd)

    @rule(IrBinary, op="mul")
    @rule(IrBinary, op="div")
    @rule(IrBinary, op="mod")
    @rule(IrBinary, op="min")
    @rule(IrBinary, op="max")
    def binary_score_only(
        self, node: IrBinary, result: list[str]
    ) -> Generator[IrNode, str, None]:
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

        result.append(cmd)

    @rule(IrBinary, op="append")
    def append(self, node: IrBinary, result: list[str]) -> Generator[IrNode, str, None]:
        left = yield node.left
        right = yield node.right

        match node.left, node.right:
            case IrData(), IrLiteral():
                cmd = f"data modify {left} append value {right}"
            case IrData(), IrData():
                cmd = f"data modify {left} append from {right}"
            case l, r:
                raise InvalidOperand(node.op, l, r)

        result.append(cmd)

    @rule(IrBinary, op="prepend")
    def prepend(
        self, node: IrBinary, result: list[str]
    ) -> Generator[IrNode, str, None]:
        left = yield node.left
        right = yield node.right

        match node.left, node.right:
            case IrData(), IrLiteral():
                cmd = f"data modify {left} prepend value {right}"
            case IrData(), IrData():
                cmd = f"data modify {left} prepend from {right}"
            case l, r:
                raise InvalidOperand(node.op, l, r)

        result.append(cmd)

    @rule(IrInsert)
    def insert(self, node: IrInsert, result: list[str]) -> Generator[IrNode, str, None]:
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

        result.append(cmd)

    @rule(IrBinary, op="merge")
    def merge(self, node: IrBinary, result: list[str]) -> Generator[IrNode, str, None]:
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

        result.append(cmd)

    @rule(IrUnary, op="remove")
    def remove(self, node: IrUnary, result: list[str]) -> Generator[IrNode, str, None]:
        target = yield node.target

        match node.target:
            case IrData():
                cmd = f"data remove {target}"
            case t:
                raise InvalidOperand(node.op, t)

        result.append(cmd)

    @rule(IrUnary, op="reset")
    def reset_op(
        self, node: IrUnary, result: list[str]
    ) -> Generator[IrNode, str, None]:
        target = yield node.target

        match node.target:
            case IrScore():
                cmd = f"scoreboard players reset {target}"
            case t:
                raise InvalidOperand(node.op, t)

        result.append(cmd)

    @rule(IrUnary, op="enable")
    def enable(self, node: IrUnary, result: list[str]) -> Generator[IrNode, str, None]:
        target = yield node.target

        match node.target:
            case IrScore():
                cmd = f"scoreboard players enable {target}"
            case t:
                raise InvalidOperand(node.op, t)

        result.append(cmd)

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
    def set(self, node: IrBinary, result: list[str]) -> Generator[IrNode, str, None]:
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

        result.append(cmd)

    @rule(IrCast, op="cast")
    def cast(self, node: IrCast, result: list[str]) -> Generator[IrNode, str, None]:
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

        result.append(cmd)
