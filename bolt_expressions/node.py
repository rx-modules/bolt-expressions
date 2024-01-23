from abc import ABC, abstractmethod
from contextlib import contextmanager
from dataclasses import dataclass, field
from functools import partial
from typing import Generator, Iterable, Union

from beet import Context, Function
from bolt import Runtime
from mecha import Mecha
from pydantic import BaseModel
from nbtlib import Path # type: ignore

from .optimizer import (
    ConstScoreManager,
    DataTuple,
    IrData,
    IrLiteral,
    IrOperation,
    IrScore,
    IrSource,
    NbtValue,
    Optimizer,
    ScoreTuple,
    TempScoreManager,
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
    rename_temp_scores,
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

class Expression:
    ctx: Context | None
    opts: ExpressionOptions

    called_init: bool
    init_commands: list[str]
    commands: list[str] | None

    optimizer: Optimizer
    serializer: IrSerializer

    temp_score: TempScoreManager
    const_score: ConstScoreManager
    identifiers: Generator[str, None, None]

    mecha: Mecha | None
    runtime: Runtime | None

    def __init__(
        self,
        ctx: Context | None = None,
        opts: ExpressionOptions | None = None,
        mc: Mecha | None = None,
        runtime: Runtime | None = None,
    ):
        self.called_init = False
        self.init_commands = []
        self.commands = None

        self.ctx = ctx

        if self.ctx:
            self.opts = self.ctx.inject(expression_options)
            self.identifiers = identifier_generator(ctx)
            self.mc = self.ctx.inject(Mecha)
            self.runtime = self.ctx.inject(Runtime)
        else:
            self.opts = opts if opts is not None else ExpressionOptions()
            self.identifiers = identifier_generator()
            self.mc = mc
            self.runtime = runtime

        self.temp_score = TempScoreManager(self.opts.temp_objective)
        self.const_score = ConstScoreManager(self.opts.const_objective)

        self.optimizer = Optimizer(
            temp_score=self.temp_score,
            const_score=self.const_score,
            default_floating_nbt_type=self.opts.default_floating_nbt_type,
        )
        self.optimizer.add_rules(
            data_insert_score,
            # features
            partial(data_set_scaling, opt=self.optimizer),
            data_get_scaling,
            # optimize
            noncommutative_set_collapsing,
            commutative_set_collapsing,
            partial(convert_data_arithmetic, self.optimizer),
            apply_temp_source_reuse,
            # cleanup
            multiply_divide_by_fraction,
            multiply_divide_by_one_removal,
            add_subtract_by_zero_removal,
            set_to_self_removal,
            set_and_get_cleanup,
            partial(rename_temp_scores, self.optimizer),
            partial(literal_to_constant_replacement, self.optimizer),
        )

        self.serializer = IrSerializer(default_nbt_type=self.opts.default_nbt_type)

    
    def temp_data(self) -> DataTuple:
        name = next(self.identifiers)
        return DataTuple("storage", self.opts.temp_storage, Path(name))

    def inject_command(self, *cmds: str):
        if self.commands is not None:
            self.commands.extend(cmds)
            return

        if self.mc and self.runtime:
            for cmd in cmds:
                self.runtime.commands.append(self.mc.parse(cmd, using="command"))

    @contextmanager
    def scope(self, result: list[str] | None = None):
        if result is None:
            result = []

        prev = self.commands
        self.commands = result

        yield self.commands

        self.commands = prev

    def resolve(self, node: ExpressionNode) -> ResolveResult:
        self.temp_score.reset()

        # pprint(node)

        unrolled_nodes, output = node.unroll()
        # pprint(unrolled_nodes)

        optimized_nodes = list(self.optimizer(unrolled_nodes))
        # pprint(optimized_nodes)

        cmds = self.serializer(optimized_nodes)
        # pprint(cmds, expand_all=True)

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
        if not self.ctx:
            return

        path = self.ctx.generate.path(self.opts.init_path)
        self.inject_command(f"function {path}")
        self.called_init = True

    def generate_init(self) -> Function:
        function = Function(
            self.init_commands,
            prepend_tags=["minecraft:load"] if not self.called_init else None,
        )

        if not self.init_commands:
            return function

        if self.ctx:
            self.ctx.generate(self.opts.init_path, function)
        
        return function

