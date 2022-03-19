from dataclasses import dataclass, field
from functools import cached_property
from typing import Iterable, List, Union

from rich.pretty import pprint

from beet import Context
from mecha import Mecha
from mecha.contrib.bolt import Runtime

from .node import ExpressionNode
from .sources import ScoreSource
from .operations import Operation, Set
from .optimizer import Optimizer
from . import resolver

def minn(arg1: ExpressionNode, arg2: ExpressionNode):
    return arg1 < arg2

def maxx(arg1: ExpressionNode, arg2: ExpressionNode):
    return arg1 > arg2

@dataclass
class Scoreboard:
    ctx: Context

    @cached_property
    def _runtime(self) -> Runtime:
        return self.ctx.inject(Runtime)

    @cached_property
    def _mc(self) -> Mecha:
        return self.ctx.inject(Mecha)

    def inject_command(self, cmd: str):
        self._runtime.commands.append(self._mc.parse(cmd, using="command"))

    def resolve(self, value: Operation):
        nodes = list(value.unroll())
        pprint(nodes)
        optimized = list(Optimizer.optimize(nodes))
        pprint(optimized)
        cmds = list(resolver.resolve(optimized))
        # pprint(cmds, expand_all=True)
        for cmd in cmds: self.inject_command(cmd)

    def set_score(self, score: ScoreSource, value: ExpressionNode):
        Set.create(score, value).resolve()

    def __call__(self, objective: str):
        Set.on_resolve(self.resolve)
        ScoreSource.on_rebind(self.set_score)
        self._runtime.expose("minn", min)
        self._runtime.expose("maxx", max)
        return Score(self, objective)


@dataclass
class Score:
    ref: Scoreboard = field(repr=False)
    objective: str

    def __getitem__(self, scoreholder: str) -> ExpressionNode:
        return ScoreSource.create(scoreholder, self.objective)

    def __setitem__(self, scoreholder: str, value: Operation):
        self.ref.set_score(self[scoreholder], value)
    
    def __str__(self):
        return self.objective
