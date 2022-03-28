from dataclasses import dataclass, field
from functools import cached_property
from typing import Iterable, List, Union

from beet import Context, Function, FunctionTag
from mecha import Mecha
from mecha.contrib.bolt import Runtime
from pydantic import BaseModel

from . import resolver
from .node import ExpressionNode
from .operations import GenericValue, Operation, Set, wrapped_max, wrapped_min
from .optimizer import Optimizer
from .sources import ConstantScoreSource, ScoreSource, Source, TempScoreSource


class ExpressionOptions(BaseModel):
    """Bolt Expressions Options"""

    temp_objective: str = "bolt.expr.temp"
    const_objective: str = "bolt.expr.const"
    init_path: str = "init_expressions"


@dataclass
class Expression:
    ctx: Context
    activated: bool = False
    called_init: bool = False
    init_commands: List[str] = field(default_factory=list)

    def __post_init__(self):
        if not self.activated:
            self.opts = self.ctx.validate("bolt_expressions", ExpressionOptions)
            self._runtime.expose("min", wrapped_min)
            self._runtime.expose("max", wrapped_max)
            self.activated = True

        Set.on_resolve(self.resolve)
        TempScoreSource.objective = self.opts.temp_objective
        ConstantScoreSource.objective = self.opts.const_objective

        self.init_commands.append(
            f"scoreboard objectives add {self.opts.temp_objective} dummy"
        )
        self.init_commands.append(
            f"scoreboard objectives add {self.opts.const_objective} dummy"
        )

    @cached_property
    def _runtime(self) -> Runtime:
        return self.ctx.inject(Runtime)

    @cached_property
    def _mc(self) -> Mecha:
        return self.ctx.inject(Mecha)

    def _inject_command(self, cmd: str):
        self._runtime.commands.append(self._mc.parse(cmd, using="command"))

    def resolve(self, value: Operation):
        nodes = list(value.unroll())
        # pprint(nodes)
        optimized = list(Optimizer.optimize(nodes))
        # pprint(optimized)
        cmds = list(resolver.resolve(optimized))
        # pprint(cmds, expand_all=True)
        for cmd in cmds:
            self._inject_command(cmd)

    def set(self, source: Source, value: GenericValue):
        Set.create(source, value).resolve()

    def objective(self, name: str):
        """Get a Score instance through the Scoreboard API"""
        return self.ctx.inject(Scoreboard)(name)

    def init(self):
        """Injects a function which creates `ConstantSource` fakeplayers"""
        self._inject_command(f"function {self.opts.const_objective}")
        self.called_init = True

    def generate_init(self):
        scoreboard = self.ctx.inject(Scoreboard)
        path = self.ctx.generate.path(self.opts.init_path)
        self.ctx.data[path] = Function(self.init_commands)
        if not self.called_init:
            if tag := self.ctx.data.function_tags.get("minecraft:load", None):
                tag["values"].insert(0, path)
            else:
                self.ctx.data.function_tags["minecraft:load"] = FunctionTag(
                    {"values": [path]}
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
    constants: List[str] = field(default_factory=list)

    def __post_init__(self):
        self._expr = self.ctx.inject(Expression)
        ConstantScoreSource.on_created(self.add_constant)
        ScoreSource.on_rebind(self.set_score)

    def add_constant(self, node: ConstantScoreSource):
        self._expr.init_commands.append(
            f"scoreboard players set {node} {int(node.scoreholder[1:])}"
        )

    def set_score(self, score: ScoreSource, value: GenericValue):
        return self._expr.set(score, value)

    def __call__(self, objective: str):
        return Score(self, objective)


@dataclass
class Score:
    ref: Scoreboard = field(repr=False)
    objective: str

    def __getitem__(self, scoreholder: str) -> ScoreSource:
        return ScoreSource.create(scoreholder, self.objective)

    def __setitem__(self, scoreholder: str, value: Operation):
        self.ref.set_score(self[scoreholder], value)

    def __str__(self):
        return self.objective
