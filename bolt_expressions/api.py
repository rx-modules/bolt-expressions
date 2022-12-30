from dataclasses import dataclass, field
from functools import cached_property, partial
from typing import Iterable, List, Union

from beet import Context, Function, FunctionTag
from bolt import Runtime
from mecha import Mecha
from pydantic import BaseModel

from . import resolver
from .ast import ConstantScoreChecker, ObjectiveChecker, SourceJsonConverter
from .literals import literal_types
from .node import ExpressionNode
from .operations import (
    Append,
    GenericValue,
    Insert,
    Merge,
    MergeRoot,
    Operation,
    Prepend,
    Set,
    wrapped_max,
    wrapped_min,
)
from .optimizer import Optimizer
from .sources import (
    ConstantScoreSource,
    DataSource,
    ScoreSource,
    Source,
    TempScoreSource,
)
from .utils import identifier_generator

# from rich import print
# from rich.pretty import pprint

__all__ = [
    "ExpressionOptions",
    "Expression",
    "Scoreboard",
    "Score",
    "Data",
]


class ExpressionOptions(BaseModel):
    """Bolt Expressions Options"""

    temp_objective: str = "bolt.expr.temp"
    const_objective: str = "bolt.expr.const"
    temp_storage: str = "bolt.expr:temp"
    init_path: str = "init_expressions"
    objective_prefix: str = ""

    disable_commands: bool = False


@dataclass
class Expression:
    ctx: Context
    activated: bool = False
    called_init: bool = False
    init_commands: List[str] = field(default_factory=list)

    def __post_init__(self):
        if not self.activated:
            self.opts = self.ctx.validate("bolt_expressions", ExpressionOptions)
            self._runtime.expose(
                "min", partial(wrapped_min, self._runtime.globals.get("min", min))
            )
            self._runtime.expose(
                "max", partial(wrapped_max, self._runtime.globals.get("max", max))
            )
            self.activated = True

        if not self.opts.disable_commands:
            self.ctx.require("bolt_expressions.contrib.commands")

        helpers = self._runtime.helpers

        helpers["interpolate_json"] = SourceJsonConverter(helpers["interpolate_json"])

        Set.on_resolve(self.resolve)
        TempScoreSource.objective = self.opts.temp_objective
        ConstantScoreSource.objective = self.opts.const_objective

    @cached_property
    def _runtime(self) -> Runtime:
        return self.ctx.inject(Runtime)

    @cached_property
    def _mc(self) -> Mecha:
        return self.ctx.inject(Mecha)

    def _inject_command(self, cmd: str):
        self._runtime.commands.append(self._mc.parse(cmd, using="command"))

    def resolve(self, nodes: Operation):
        # pprint(nodes)
        nodes = list(nodes.unroll())
        # pprint(nodes)
        nodes = list(Optimizer.optimize(nodes))
        # pprint(nodes)
        cmds = list(resolver.resolve(nodes))
        # pprint(cmds, expand_all=True)
        for cmd in cmds:
            self._inject_command(cmd)

    def set(self, source: Source, value: GenericValue):
        Set.create(source, value).resolve()

    def init(self):
        """Injects a function which creates `ConstantSource` fakeplayers"""
        path = self.ctx.generate.path(self.opts.init_path)
        self._inject_command(f"function {path}")
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


@dataclass
class Scoreboard:
    """API for manipulating scoreboards.

    To use, inject the current `Context` and construct an `Score` instance.
    ```
        Objective = ctx.inject(Scoreboard)
        my_obj = Objective["my_obj"]
    ```
    Now you can perform the API manipulation via the operators:
    ```
        my_obj["@s"] += 10
        my_obj["temp"] = my_obj["@s"] * 10
        player = my_obj["@s"]
        player += 10 * my_obj["temp"]
    ```
    """

    ctx: Context
    objectives: set[str] = field(default_factory=set)
    constants: set[int] = field(default_factory=set)

    added_objectives: set[str] = field(init=False, default_factory=set)

    def __post_init__(self):
        self._expr = self.ctx.inject(Expression)

        opts = self._expr.opts

        self.objectives.update((opts.const_objective, opts.temp_objective))

        self._expr._mc.check.extend(
            ConstantScoreChecker(
                objective=opts.const_objective, callback=self.add_constant
            ),
            ObjectiveChecker(
                whitelist=self.objectives,
                callback=self.add_objective,
            ),
        )
        ScoreSource.on_rebind(self.set_score)
        ScoreSource.attach("reset", self.reset)
        ScoreSource.attach("enable", self.enable)

    def add_objective(self, name: str, criteria: str = "dummy"):
        if name not in self.added_objectives:
            self.added_objectives.add(name)

            self._expr.init_commands.insert(
                0, f"scoreboard objectives add {name} {criteria}"
            )

    def add_constant(self, node: ConstantScoreSource):
        if not node.value in self.constants:
            self.constants.add(node.value)
            self._expr.init_commands.append(
                f"scoreboard players set {node} {node.value}"
            )

    def set_score(self, score: ScoreSource, value: GenericValue):
        return self._expr.set(score, value)

    def objective(self, name: str, criteria: str = None, prefixed=True):
        """Get a Score instance through the Scoreboard API"""
        if prefixed:
            name = self._expr.opts.objective_prefix + name

        if criteria:
            self.add_objective(name, criteria)

        return Score(self, name)

    def __call__(self, objective: str, criteria: str = None, prefixed=True):
        return self.objective(objective, criteria, prefixed)

    def reset(self, source: ScoreSource):
        cmd = resolver.generate("reset:score", source)
        self._expr._inject_command(cmd)

    def enable(self, source: ScoreSource):
        cmd = resolver.generate("enable:score", source)
        self._expr._inject_command(cmd)


@dataclass
class Score:
    ref: Scoreboard = field(repr=False)
    objective: str

    def __getitem__(self, scoreholder: Union[str, List[str]]) -> ScoreSource:
        if type(scoreholder) is str:
            return ScoreSource.create(scoreholder, self.objective)
        return [ScoreSource.create(holder, self.objective) for holder in scoreholder]

    def __setitem__(self, scoreholder: str, value: Operation):
        self.ref.set_score(self[scoreholder], value)

    def __str__(self):
        return self.objective


@dataclass
class Data:
    ctx: Context

    def __post_init__(self):
        self._expr = self.ctx.inject(Expression)
        self.identifiers = identifier_generator(self.ctx)
        DataSource.on_rebind(self.set_data)
        DataSource.attach("remove", self.remove)
        DataSource.attach("append", self.append)
        DataSource.attach("prepend", self.prepend)
        DataSource.attach("insert", self.insert)
        DataSource.attach("merge", self.merge)

    def __call__(self, target: str):
        """Guess target type and return a data source."""
        ...

    def set_data(self, source: DataSource, value: GenericValue):
        return self._expr.set(source, value)

    def storage(self, resource_location: str):
        return DataSource.create("storage", resource_location)

    def entity(self, entity: str):
        return DataSource.create("entity", entity)

    def block(self, position: str):
        return DataSource.create("block", position)

    def dummy(self, scale: int = 1, type: str = "int"):
        "Create a dummy data source in a storage."
        path = next(self.identifiers)
        target = self._expr.opts.temp_storage
        return DataSource.create("storage", target, path, scale, type)

    def cast(self, value: Union[Source, Operation], type: str):
        source = self.dummy(type=type)
        if not isinstance(value, ExpressionNode):
            value = literal_types[type](value)
        self._expr.set(source, value)
        return source._copy(nbt_type=None)

    def remove(self, source: DataSource, value: Union[str, int] = None):
        node = source if value is None else source[value]
        if not len(node._path):
            raise ValueError(
                f'Cannot remove the root of {node._type} "{node._target}".'
            )
        cmd = resolver.generate("remove:data", value=node)
        self._expr._inject_command(cmd)

    def append(self, source: DataSource, value: GenericValue):
        self._expr.resolve(Append.create(source, value))

    def prepend(self, source: DataSource, value: GenericValue):
        self._expr.resolve(Prepend.create(source, value))

    def insert(self, source: DataSource, index: int, value: GenericValue):
        self._expr.resolve(Insert.create(source, value, index=index))

    def merge(self, source: DataSource, value: GenericValue):
        Operation = Merge if len(source._path) else MergeRoot
        self._expr.resolve(Operation.create(source, value))
