from abc import ABC, abstractmethod
from contextlib import contextmanager
from dataclasses import dataclass, field
from enum import Enum, auto
from functools import partial
from typing import Generator, Iterable, Union

from beet import Context, Function
from bolt import Runtime
from bolt.utils import internal
from bolt.contrib.defer import Defer
from mecha import Mecha
from pydantic import BaseModel
from nbtlib import Path  # type: ignore


from .optimizer import (
    ConstScoreManager,
    IrData,
    IrLiteral,
    IrOperation,
    IrScore,
    IrSource,
    NbtValue,
    Optimizer,
    SourceTuple,
    TempDataManager,
    TempScoreManager,
    add_subtract_by_zero_removal,
    commutative_set_collapsing,
    convert_data_arithmetic,
    convert_cast,
    data_get_scaling,
    data_insert_score,
    data_set_scaling,
    discard_casting,
    literal_to_constant_replacement,
    multiply_divide_by_fraction,
    multiply_divide_by_one_removal,
    noncommutative_set_collapsing,
    apply_temp_source_reuse,
    rename_temp_scores,
    set_and_get_cleanup,
    set_to_self_removal,
)
from .typing import NbtTypeString
from .casting import TypeCaster
from .check import TypeChecker
from .serializer import IrSerializer
from .utils import identifier_generator


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


class ResultType(Enum):
    score = auto()
    data = auto()


@dataclass
class UnrollHelper:
    ignored_sources: set[SourceTuple] = field(init=False, default_factory=set)
    temporaries: set[SourceTuple] = field(init=False, default_factory=set)

    score_manager: TempScoreManager
    data_manager: TempDataManager

    @contextmanager
    def ignore_source(self, source: SourceTuple):
        remove = source not in self.ignored_sources
        self.ignored_sources.add(source)

        yield

        if remove:
            self.ignored_sources.remove(source)

    def add_temporary(self, source: SourceTuple):
        self.temporaries.add(source)

    def create_temporary(self, result: ResultType) -> IrSource:
        if result == ResultType.data:
            source = self.data_manager()
            self.add_temporary(source)
            return IrData(type=source.type, target=source.target, path=source.path)

        source = self.score_manager()
        self.add_temporary(source)
        return IrScore(holder=source.holder, obj=source.obj)


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
    def unroll(
        self, helper: UnrollHelper
    ) -> tuple[Iterable[IrOperation], IrSource | IrLiteral]:
        ...


ResolveResult = SourceTuple | NbtValue | None


@dataclass(kw_only=True)
class LazyEntry:
    source: SourceTuple
    node: ExpressionNode
    commands: list[str]
    emit: bool = False


class Expression:
    ctx: Context | None
    opts: ExpressionOptions

    called_init: bool
    init_commands: list[str]
    commands: list[str] | None
    lazy_values: dict[SourceTuple, LazyEntry]

    type_caster: TypeCaster
    type_checker: TypeChecker
    optimizer: Optimizer
    serializer: IrSerializer

    temp_score: TempScoreManager
    temp_data: TempDataManager
    const_score: ConstScoreManager
    identifiers: Generator[str, None, None]

    mecha: Mecha | None
    runtime: Runtime | None
    defer: Defer | None

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
        self.lazy_values = {}

        self.ctx = ctx

        if self.ctx:
            self.opts = self.ctx.inject(expression_options)
            self.identifiers = identifier_generator(ctx)
            self.mc = self.ctx.inject(Mecha)
            self.runtime = self.ctx.inject(Runtime)
            self.defer = self.ctx.inject(Defer)
        else:
            self.opts = opts if opts is not None else ExpressionOptions()
            self.identifiers = identifier_generator()
            self.mc = mc
            self.runtime = runtime

        self.temp_score = TempScoreManager(
            self.opts.temp_objective, format=lambda _: "$" + next(self.identifiers)
        )
        self.temp_data = TempDataManager(
            "storage", self.opts.temp_storage, format=lambda _: next(self.identifiers)
        )
        self.const_score = ConstScoreManager(self.opts.const_objective)

        self.type_caster = TypeCaster(ctx=self.ctx)
        self.type_checker = TypeChecker(ctx=self.ctx)

        self.optimizer = Optimizer(
            temp_score=self.temp_score,
            temp_data=self.temp_data,
            const_score=self.const_score,
            default_floating_nbt_type=self.opts.default_floating_nbt_type,
        )
        self.optimizer.add_rules(
            data_insert_score,
            convert_cast,
            partial(convert_data_arithmetic, self.optimizer),
            discard_casting,
            partial(apply_temp_source_reuse, self.optimizer),
            set_to_self_removal,
            # features
            partial(data_set_scaling, opt=self.optimizer),
            data_get_scaling,
            # cleanup
            multiply_divide_by_fraction,
            multiply_divide_by_one_removal,
            add_subtract_by_zero_removal,
            set_to_self_removal,
            set_and_get_cleanup,
            noncommutative_set_collapsing,
            commutative_set_collapsing,
            partial(rename_temp_scores, self.optimizer),
            partial(literal_to_constant_replacement, self.optimizer),
            # typing
            self.type_caster,
            self.type_checker,
        )

        self.serializer = IrSerializer(default_nbt_type=self.opts.default_nbt_type)

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

    @internal
    def resolve(self, node: ExpressionNode, lazy: bool = False):
        helper = UnrollHelper(
            score_manager=self.temp_score, data_manager=self.temp_data
        )
        operations, result = node.unroll(helper)

        if not isinstance(result, IrSource):
            return

        source = result.to_tuple()

        if source in self.lazy_values:
            del self.lazy_values[source]

        with self.optimizer.temp(*helper.temporaries):
            optimized_nodes = list(self.optimizer(operations))

        cmds = self.serializer(optimized_nodes)

        if not lazy or not self.defer:
            self.inject_command(*cmds)
            return

        entry = LazyEntry(source=source, node=node, commands=cmds)
        self.lazy_values[source] = entry
        self.defer(partial(self.emit_lazy, entry=entry))

    def unroll_lazy(
        self, source: SourceTuple, helper: UnrollHelper
    ) -> tuple[Iterable[IrOperation], IrSource | IrLiteral] | None:
        if source in helper.ignored_sources:
            return None

        if entry := self.lazy_values.get(source):
            helper.add_temporary(source)

            with helper.ignore_source(source):
                return entry.node.unroll(helper)

        return None

    def evaluate_lazy(self, source: SourceTuple):
        if entry := self.lazy_values.get(source):
            entry.emit = True
            del self.lazy_values[source]

    def emit_lazy(self, entry: LazyEntry):
        if entry.emit:
            self.inject_command(*entry.commands)

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
