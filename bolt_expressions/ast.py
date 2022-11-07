from dataclasses import dataclass, field
from functools import cached_property
from typing import Callable, Iterable, List

from beet.core.utils import required_field
from mecha import AstCommand, AstObjective, AstPlayerName, Reducer, rule

from .sources import ConstantScoreSource


@dataclass
class ConstantScoreChecker(Reducer):
    objective: str = required_field()
    callback: Callable = required_field()

    @cached_property
    def objective_node(self):
        return AstObjective(value=self.objective)

    @rule(AstCommand)
    def command(self, node: AstCommand):
        if self.objective_node not in node.arguments:
            return

        i = node.arguments.index(self.objective_node)
        name = node.arguments[i - 1]

        if not isinstance(name, AstPlayerName):
            return

        value = name.value

        if not (value.startswith("$") and value[1:].isdigit()):
            return

        value = int(value[1:])
        source = ConstantScoreSource.create(value)

        self.callback(source)


@dataclass
class ObjectiveChecker(Reducer):
    whitelist: Iterable[str] = required_field()
    callback: Callable = required_field()

    @rule(AstObjective)
    def objective(self, node: AstObjective):
        value = node.value

        if value not in self.whitelist:
            return

        self.callback(value)
