from dataclasses import dataclass, field
from functools import cached_property
from typing import Iterable, List, Union

from beet import Context
from mecha import Mecha
from mecha.contrib.bolt import Runtime
from rich import print
from rich.pretty import pprint

from . import resolver
from .node import ExpressionNode
from .operations import Operation, Set
from .optimizer import Optimizer
from .sources import ScoreSource


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
        return Score(self, scoreholder)

    def test(self):
        print(self.ctx)


@dataclass
class Score:
    ref: Scoreboard = field(repr=False)
    objective: str

    def __getitem__(self, scoreholder: str) -> ExpressionNode:
        return ScoreSource.create(scoreholder, self.objective)

    def __setitem__(self, scoreholder: str, value: Operation):
        self.resolve(Set.create(self[scoreholder], value))

    def optimize(self, nodes: Iterable[Operation]) -> List[Operation]:
        ...

    def resolve(self, root: Operation):
        nodes = list(root.unroll())
        pprint(nodes)
        optimized = list(Optimizer.optimize(nodes))
        pprint(optimized)
        cmds = list(resolver.resolve(optimized))
        # pprint(cmds, expand_all=True)

        list(map(self.ref.inject_command, cmds))
