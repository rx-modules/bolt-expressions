from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from functools import cached_property, partial
from typing import Generator, Iterable, Union

from beet import Context, Function
from bolt import Runtime
from mecha import Mecha
from pydantic import BaseModel
from nbtlib import Path

from .optimizer import (
    DataTuple,
    IrData,
    IrLiteral,
    IrOperation,
    IrScore,
    IrSource,
    NbtValue,
    Optimizer,
    ScoreTuple,
    add_subtract_by_zero_removal,
    commutative_set_collapsing,
    convert_data_arithmetic,
    data_get_scaling,
    data_insert_score,
    data_set_scaling,
    literal_to_constant_replacement,
    multiply_divide_by_fraction,
    multiply_divide_by_one_removal,
    noncommutative_set_collapsing,
    apply_temp_source_reuse,
    set_and_get_cleanup,
    set_to_self_removal,
)
from .serializer import IrSerializer
from .typing import NbtTypeString
from .utils import identifier_generator

from rich.pretty import pprint

__all__ = [
    "ExpressionOptions",
    "expression_options",
    "TempScoreManager",
    "ConstScoreManager",
    "ExpressionNode",
    "Expression",
]


class ExpressionOptions(BaseModel):
    """Bolt Expressions Options"""

    temp_objective: str = "bolt.expr.temp"
    const_objective: str = "bolt.expr.const"
    temp_storage: str = "bolt.expr:temp"
    init_path: str = "init_expressions"
    objective_prefix: str = ""
    default_nbt_type: NbtTypeString = "int"
    default_floating_nbt_type: str = "double"

    disable_commands: bool = False


def expression_options(ctx: Context) -> ExpressionOptions:
    return ctx.validate("bolt_expressions", ExpressionOptions)


@dataclass
class TempScoreManager:
    objective: str

    counter: int = field(default=0, init=False)

    def __call__(self) -> ScoreTuple:
        name = f"$s{self.counter}"
        self.counter += 1

        return ScoreTuple(name, self.objective)

    def reset(self):
        self.counter = 0


@dataclass
class ConstScoreManager:
    objective: str

    constants: set[int] = field(default_factory=set, init=False)

    def format(self, value: int) -> str:
        return f"${value}"

    def create(self, value: int) -> ScoreTuple:
        self.constants.add(value)

        return ScoreTuple(self.format(value), self.objective)

    __call__ = create


@dataclass(order=False, eq=False, kw_only=True)
class ExpressionNode(ABC):
    ctx: Union[Context, "Expression"] = field(repr=False)
    expr: "Expression" = field(init=False, repr=False)

    def __post_init__(self):
        if isinstance(self.ctx, Expression):
            self.expr = self.ctx
        else:
            self.expr = self.ctx.inject(Expression)
        

    @abstractmethod
    def unroll(self) -> tuple[Iterable[IrOperation], IrSource | IrLiteral]:
        ...


ResolveResult = ScoreTuple | DataTuple | NbtValue | None

@dataclass
class Expression:
    ctx: Context = field(repr=False)
    called_init: bool = False
    init_commands: list[str] = field(default_factory=list)

    optimizer: Optimizer = field(init=False)
    serializer: IrSerializer = field(init=False)

    temp_score: TempScoreManager = field(init=False)
    const_score: ConstScoreManager = field(init=False)

    identifiers: Generator[str, None, None] = field(init=False)

    def __post_init__(self):
        self.opts = self.ctx.inject(expression_options)

        self.temp_score = TempScoreManager(self.opts.temp_objective)
        self.const_score = ConstScoreManager(self.opts.const_objective)

        self.optimizer = Optimizer(
            temp_score=self.temp_score,
            const_score=self.const_score,
            default_floating_nbt_type=self.opts.default_floating_nbt_type,
        )
        self.optimizer.add_rules(
            data_insert_score,
            partial(convert_data_arithmetic, self.optimizer),
            # features
            partial(data_set_scaling, opt=self.optimizer),
            data_get_scaling,
            multiply_divide_by_fraction,
            # optimize
            noncommutative_set_collapsing,
            commutative_set_collapsing,
            apply_temp_source_reuse,
            # cleanup
            multiply_divide_by_one_removal,
            add_subtract_by_zero_removal,
            set_to_self_removal,
            set_and_get_cleanup,
            partial(literal_to_constant_replacement, self.optimizer),
        )

        self.serializer = IrSerializer(default_nbt_type=self.opts.default_nbt_type)

        self.identifiers = identifier_generator(self.ctx)
    
    def temp_data(self) -> DataTuple:
        name = next(self.identifiers)
        return DataTuple("storage", self.opts.temp_storage, Path(name))

    @cached_property
    def _runtime(self) -> Runtime:
        return self.ctx.inject(Runtime)

    @cached_property
    def _mc(self) -> Mecha:
        return self.ctx.inject(Mecha)

    def inject_command(self, *cmds: str):
        for cmd in cmds:
            self._runtime.commands.append(self._mc.parse(cmd, using="command"))

    def resolve(self, node: ExpressionNode) -> ResolveResult:
        self.temp_score.reset()

        pprint(node)

        unrolled_nodes, output = node.unroll()
        # pprint(unrolled_nodes)

        optimized_nodes = list(self.optimizer(unrolled_nodes))
        pprint(optimized_nodes)

        cmds = self.serializer(optimized_nodes)
        pprint(cmds, expand_all=True)

        self.inject_command(*cmds)

        match output:
            case IrScore() as s:
                result = ScoreTuple(s.holder, s.obj)
            case IrData() as d:
                result = DataTuple(d.type, d.target, d.path, d.nbt_type)
            case IrLiteral() as l:
                result = l.value
            case _:
                result = None
        
        return result
            

    def init(self):
        """Injects a function which creates `ConstantSource` fakeplayers"""
        path = self.ctx.generate.path(self.opts.init_path)
        self.inject_command(f"function {path}")
        self.called_init = True

    def generate_init(self):
        if not self.init_commands:
            return

        self.ctx.generate(
            self.opts.init_path,
            Function(
                self.init_commands,
                prepend_tags=["minecraft:load"] if not self.called_init else None,
            ),
        )

