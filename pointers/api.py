from dataclasses import dataclass, field
from functools import cached_property
from typing import Iterable, List, Union

from beet import Context
from mecha import Mecha
from mecha.contrib.bolt import Runtime


from .node import ExpressionNode
from .operations import Operation, Set
from .sources import ScoreSource

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

    def __call__(self, scoreholder):
        ExpressionNode.inject_command = self.inject_command
        self._runtime.expose("minn", min)
        self._runtime.expose("maxx", max)
        return Score(self, scoreholder)


@dataclass
class Score:
    ref: Scoreboard = field(repr=False)
    objective: str

    def __getitem__(self, scoreholder: str) -> ExpressionNode:
        return ScoreSource.create(scoreholder, self.objective)

    def __setitem__(self, scoreholder: str, value: Operation):
        Set.create(self[scoreholder], value).resolve()
