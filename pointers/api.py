from dataclasses import dataclass, field
from functools import cached_property
from typing import Iterable, Union, List

from beet import Context
from mecha import Mecha
from mecha.contrib.bolt import Runtime

from rich import print
from rich.pretty import pprint

from .operations import ScoreSource, ExpressionNode, Set, Operation
from . import resolver

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
        print("[bold]Tree[/bold]:")
        print(root, "\n")
        print("[bold]Unrolling[/bold]:")
        nodes = list(root.unroll())  # generator, not consumed
        print("\n", "[bold]Unrolled Nodes[/bold]:", sep="")
        pprint(nodes, expand_all=True)
        print("\n", "[bold]Resolved Cmds[/bold]:", sep="")
        cmds = list(resolver.resolve(nodes))
        pprint(cmds, expand_all=True)

        list(map(self.ref.inject_command, cmds))
