from dataclasses import dataclass
from functools import cached_property
from typing import Callable
from mecha import MutatingReducer, Reducer, rule, AstCommand, AstObjective
from beet.core.utils import required_field

from .sources import ConstantScoreSource


@dataclass
class ExecuteTransformer(MutatingReducer):
    @rule(AstCommand, identifier="execute:run:subcommand")
    def strip_run_execute(self, node: AstCommand):
        if isinstance(command := node.arguments[0], AstCommand):
            if command.identifier == "execute:subcommand":
                return command.arguments[0]
        return node


@dataclass
class ConstantScoreChecker(Reducer):
    objective: str = required_field()
    callback: Callable = required_field()

    @cached_property
    def objective_node(self):
        return AstObjective(value=self.objective)

    @rule(AstCommand)
    def command(self, node: AstCommand):
        if self.objective_node in node.arguments:
            i = node.arguments.index(self.objective_node)
            name = node.arguments[i - 1]
            source = ConstantScoreSource.from_name(name.value)
            self.callback(source)
