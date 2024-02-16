from abc import ABC, abstractmethod
from contextlib import contextmanager
from dataclasses import dataclass, field
from enum import Enum, auto
from functools import partial
from typing import Iterable, Union
import typing as t

from beet import Context, Generator, Function
from bolt import Runtime
from bolt.utils import internal
from bolt.contrib.defer import Defer
from mecha import AstChildren, AstCommand, AstRoot, Mecha
from mecha.contrib.nested_location import NestedLocationResolver
from pydantic import BaseModel
from nbtlib import Path  # type: ignore


from .optimizer import (
    ConstScoreManager,
    IrBranch,
    IrChildren,
    IrData,
    IrLiteral,
    IrOperation,
    IrScore,
    IrSet,
    IrSource,
    NbtValue,
    Optimizer,
    SourceTuple,
    TempDataManager,
    TempScoreManager,
    add_subtract_by_zero_removal,
    commutative_set_collapsing,
    branch_condition_propagation,
    convert_data_arithmetic,
    convert_cast,
    compound_match_data_compare,
    convert_data_order_operation,
    convert_defined_boolean_condition,
    data_get_scaling,
    data_insert_score,
    data_set_scaling,
    deadcode_elimination,
    discard_casting,
    init_score_boolean_result,
    literal_to_constant_replacement,
    multiply_divide_by_fraction,
    multiply_divide_by_one_removal,
    noncommutative_set_collapsing,
    apply_temp_source_reuse,
    boolean_condition_propagation,
    rename_temp_scores,
    set_and_get_cleanup,
    set_to_self_removal,
    store_set_data_compare,
)
from .typing import NbtTypeString
from .casting import TypeCaster
from .check import TypeChecker
from .ast_converter import AstConverter
from .utils import identifier_generator, insert_nested_commands


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

    def remove_temporary(self, source: SourceTuple):
        self.temporaries.discard(source)

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
    commands: AstChildren[AstCommand]
    emit: bool = False


class Expression:
    ctx: Context
    opts: ExpressionOptions

    called_init: bool
    init_commands: list[str]
    commands: list[AstCommand] | None
    lazy_values: dict[SourceTuple, LazyEntry]

    type_caster: TypeCaster
    type_checker: TypeChecker
    optimizer: Optimizer
    ast_converter: AstConverter

    temp_score: TempScoreManager
    temp_data: TempDataManager
    const_score: ConstScoreManager
    identifiers: t.Generator[str, None, None]

    mecha: Mecha
    runtime: Runtime
    defer: Defer
    nested_location: NestedLocationResolver
    generator: Generator

    def __init__(self, ctx: Context):
        self.called_init = False
        self.init_commands = []
        self.commands = None
        self.lazy_values = {}

        self.ctx = ctx

        self.opts = self.ctx.inject(expression_options)
        self.identifiers = identifier_generator(ctx)
        self.mc = self.ctx.inject(Mecha)
        self.runtime = self.ctx.inject(Runtime)
        self.defer = self.ctx.inject(Defer)
        self.nested_location = self.ctx.inject(NestedLocationResolver)
        self.generator = self.ctx.generate

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
            data_insert_score=data_insert_score,
            convert_cast=convert_cast,
            compound_match_data_compare=partial(
                compound_match_data_compare, opt=self.optimizer
            ),
            store_set_data_compare=partial(store_set_data_compare, opt=self.optimizer),
            convert_data_arithmetic=partial(convert_data_arithmetic, self.optimizer),
            convert_data_order_operation=partial(
                convert_data_order_operation, opt=self.optimizer
            ),
            discard_casting=discard_casting,
            init_score_boolean_result=init_score_boolean_result,
            apply_temp_source_reuse=partial(apply_temp_source_reuse, self.optimizer),
            set_to_self_removal=set_to_self_removal,
            # features
            data_set_scaling=partial(data_set_scaling, opt=self.optimizer),
            data_get_scaling=data_get_scaling,
            # cleanup
            multiply_divide_by_fraction=multiply_divide_by_fraction,
            multiply_divide_by_one_removal=multiply_divide_by_one_removal,
            add_subtract_by_zero_removal=add_subtract_by_zero_removal,
            set_to_self_removal_post=set_to_self_removal,
            set_and_get_cleanup=set_and_get_cleanup,
            noncommutative_set_collapsing=noncommutative_set_collapsing,
            commutative_set_collapsing=commutative_set_collapsing,
            literal_to_constant_replacement=partial(
                literal_to_constant_replacement, self.optimizer
            ),
            boolean_condition_propagation=boolean_condition_propagation,
            branch_condition_propagation=branch_condition_propagation,
            convert_defined_boolean_condition=partial(
                convert_defined_boolean_condition, opt=self.optimizer
            ),
            deadcode_elimination=partial(deadcode_elimination, opt=self.optimizer),
            rename_temp_scores=partial(rename_temp_scores, self.optimizer),
            # typing
            type_caster=self.type_caster,
            type_checker=self.type_checker,
        )

        self.ast_converter = AstConverter(
            default_nbt_type=self.opts.default_nbt_type, mc=self.mc
        )

    def inject_command(self, *cmds: str | AstCommand):
        commands = self.commands
        if commands is None:
            commands = self.runtime.commands

        for cmd in cmds:
            if isinstance(cmd, str):
                cmd = self.mc.parse(cmd, using="command")

            commands.append(cmd)

    @contextmanager
    def scope(self, result: list[AstCommand] | None = None):
        if result is None:
            result = []

        prev = self.commands
        self.commands = result

        yield self.commands

        self.commands = prev

    @contextmanager
    def anonymous_function(
        self, template: str = "anonymous_{incr}"
    ) -> t.Generator[str, None, None]:
        namespace, resolved = self.nested_location.resolve()
        location = self.generator.format(f"{namespace}:{resolved}/{template}")

        with self.runtime.scope() as cmds:
            yield location

        cmd = self.mc.parse(f"execute function {location}:\n  ...", using="command")
        root = AstRoot(commands=AstChildren(cmds))
        self.runtime.commands.append(insert_nested_commands(cmd, root))

    def unroll(
        self, node: ExpressionNode
    ) -> tuple[Iterable[IrOperation], IrSource | IrLiteral, UnrollHelper]:
        helper = UnrollHelper(
            score_manager=self.temp_score, data_manager=self.temp_data
        )
        operations, result = node.unroll(helper)

        if isinstance(result, IrSource):
            helper.remove_temporary(result.to_tuple())

        return operations, result, helper

    @internal
    def resolve(self, node: ExpressionNode, lazy: bool = False) -> SourceTuple:
        operations, result, helper = self.unroll(node)

        if not isinstance(result, IrSource):
            score = self.optimizer.generate_score()
            operations = (IrSet(left=score, right=result),)
            result = score

        source = result.to_tuple()

        nodes, _ = self.optimizer(operations, temporaries=helper.temporaries)
        cmds = self.ast_converter(nodes)

        if not lazy:
            self.inject_command(*cmds)
            return source

        entry = LazyEntry(source=source, node=node, commands=cmds)
        self.lazy_values[source] = entry
        self.defer(partial(self.emit_lazy, entry=entry))

        return source

    @contextmanager
    @internal
    def resolve_branch(self, node: ExpressionNode):
        operations, result, helper = self.unroll(node)

        if not isinstance(result, IrSource):
            return

        nodes, temporaries = self.optimizer(
            operations,
            temporaries=helper.temporaries,
            rename_temp_scores=False,
            deadcode_elimination=False,
        )

        with self.runtime.scope() as cmds:
            yield

        branch = IrBranch(target=result, children=IrChildren.from_ast(cmds))

        nodes, _ = self.optimizer(
            (*nodes, branch),
            disable_all=True,
            temporaries=(*temporaries, result.to_tuple()),
            branch_condition_propagation=True,
            convert_defined_boolean_condition=True,
            rename_temp_scores=True,
            deadcode_elimination=True,
        )

        cmds = self.ast_converter(nodes)
        self.inject_command(*cmds)

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

        self.ctx.generate(self.opts.init_path, function)

        return function
