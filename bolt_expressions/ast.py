import re
from dataclasses import dataclass
from functools import cached_property
from typing import Any, Callable, Iterable, cast

from beet.core.utils import required_field
from mecha import (
    AstCommand,
    AstNode,
    AstObjective,
    AstPlayerName,
    MutatingReducer,
    Reducer,
    rule,
)

from .sources import Source

__all__ = [
    "RunExecuteTransformer",
    "ConstantScoreChecker",
    "ObjectiveChecker",
    "SourceJsonConverter",
]


@dataclass
class RunExecuteTransformer(MutatingReducer):
    @rule(AstCommand, identifier="execute:run:subcommand")
    def strip_run_execute(self, node: AstCommand):
        if isinstance(command := node.arguments[0], AstCommand):
            if command.identifier == "execute:subcommand":
                return command.arguments[0]
        return node


@dataclass
class ConstantScoreChecker(Reducer):
    objective: str = required_field()
    callback: Callable[[int], None] = required_field()
    pattern: re.Pattern[str] = re.compile(r"^\$([-+]?\d+)\b")

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

        match = self.pattern.match(name.value)

        if not match:
            return

        value = int(match.group(1))
        self.callback(value)


@dataclass
class ObjectiveChecker(Reducer):
    whitelist: Iterable[str] = required_field()
    callback: Callable[[str], None] = required_field()

    @rule(AstObjective)
    def objective(self, node: AstObjective):
        value = node.value

        if value not in self.whitelist:
            return

        self.callback(value)


@dataclass
class SourceJsonConverter:
    converter: Callable[[Any, AstNode], AstNode]

    def convert(self, obj: Any) -> Any:
        if isinstance(obj, Source):
            return obj.component()

        if isinstance(obj, (list, tuple)):
            list_value = cast(list[Any], obj)
            return [self.convert(value) for value in list_value]

        if isinstance(obj, dict):
            dict_value = cast(dict[str, Any], obj)
            return {key: self.convert(value) for key, value in dict_value.items()}

        return obj

    def __call__(self, obj: Any, node: AstNode):
        obj = self.convert(obj)

        return self.converter(obj, node)
