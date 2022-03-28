from dataclasses import dataclass, field
from functools import cached_property
from typing import Iterable, List, Union

from beet import Context
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


@dataclass
class Expression:
    ctx: Context
    activated: bool = False

    def __post_init__(self):
        if not self.activated:
            self.opts = self.ctx.validate("bolt_expressions", ExpressionOptions)
            self._runtime.expose("min", wrapped_min)
            self._runtime.expose("max", wrapped_max)
            self.activated = True

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


@dataclass
class Scoreboard:
    """API for manipulating scoreboards.

    To use, inject the current `Context` and construct an `Score` instance.
    >>> Objective = ctx.inject(Scoreboard)  # doctest: +SKIP
    >>> my_obj = Objective["my_obj"]        # doctest: +SKIP

    Now you can perform the API manipulation via the operators:
    >>> my_obj["@s"] += 10                  # doctest: +SKIP
    >>> my_obj["temp"] = my_obj["@s"] * 10  # doctest: +SKIP
    >>> player = my_obj["@s"]               # doctest: +SKIP
    >>> player += 10 * my_obj["temp"]       # doctest: +SKIP
    """

    ctx: Context

    def __post_init__(self):
        self._expr = self.ctx.inject(Expression)
        ConstantScoreSource.on_created(self.add_constant)

    def add_constant(self, node: ConstantScoreSource):
        path = self.ctx.generate.path("init_expressions")
        # TODO append scoreboard set command to function path

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
