from typing import Any, Generator, Iterable
from mecha import Visitor, rule

from .utils import type_name

from .optimizer import IrBinary, IrData, IrInsert, IrLiteral, IrNode, IrScore, IrUnary


class InvalidOperand(Exception):
    def __init__(self, op: str, *operands: Any):
        fmt = ", ".join(f"'{type_name(operand)}'" for operand in operands)
        super().__init__(f"Invalid operand(s) for '{op}' operation: {fmt}.")


class IrSerializer(Visitor):
    def __call__(self, nodes: Iterable[IrNode]) -> list[str]:  # type: ignore
        result: list[str] = []

        for node in nodes:
            self.invoke(node, result)

        return result

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

    def should_cast_data(self, op: IrBinary) -> bool:
        if not isinstance(op.left, IrData):
            return False
        if not isinstance(op.right, IrData):
            return False
        
        left_scale = op.left.scale
        if left_scale is not None and left_scale != 1:
            return True

        right_scale = op.right.scale
        if right_scale is not None and right_scale != 1:
            return True

        return op.left.nbt_type is not None

    def serialize_cast(self, data: IrData) -> tuple[str, str]:
        cast_type = data.nbt_type if data.nbt_type is not None else "double"
        scale = data.scale if data.scale is not None else 1

        return (cast_type, str(scale))

    @rule(IrBinary, op="set")
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
            case IrData(), IrData() if not self.should_cast_data(node):
                cmd = f"data modify {left} set from {right}"
            case IrData() as l, IrData() as r if self.should_cast_data(node):
                nbt_type, scale = self.serialize_cast(l)
                _, right_scale = self.serialize_cast(r)
                cmd = f"execute store result {left} {nbt_type} {scale} run data get {right} {right_scale}"
            case IrData() as l, IrScore():
                nbt_type, scale = self.serialize_cast(l)
                cmd = f"execute store result {left} {nbt_type} {scale} run scoreboard players get {right}"
            case IrScore(), IrData() as r:
                _, scale = self.serialize_cast(r)
                cmd = f"execute store result score {left} run data get {right} {scale}"
            case l, r:
                raise InvalidOperand(node.op, l, r)

        result.append(cmd)
