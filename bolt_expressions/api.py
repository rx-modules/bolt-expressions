from dataclasses import dataclass, field, replace
from functools import cached_property, partial
from typing import Any, List, Union

from nbtlib import Path # type: ignore
from beet import Context

from .ast import ConstantScoreChecker, ObjectiveChecker
from .literals import literal_types
from .node import Expression, ExpressionNode
from .operations import (
    Append,
    GenericValue,
    Insert,
    Merge,
    Operation,
    Prepend,
)
from .sources import (
    DataSource,
    ScoreSource,
    Source,
)
from .utils import identifier_generator


__all__ = [
    "Scoreboard",
    "Score",
    "Data",
]


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

    ctx: Context = field(repr=False)
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

    def add_objective(self, name: str, criteria: str = "dummy"):
        if name not in self.added_objectives:
            self.added_objectives.add(name)

            self._expr.init_commands.insert(
                0, f"scoreboard objectives add {name} {criteria}"
            )

    def add_constant(self, value: int):
        const_score = self._expr.const_score
        holder, obj = const_score(value)

        if not value in self.constants:
            self.constants.add(value)
            self._expr.init_commands.append(
                f"scoreboard players set {holder} {obj} {value}"
            )

    def objective(self, name: str, criteria: str = None, prefixed=True):
        """Get a Score instance through the Scoreboard API"""
        if prefixed:
            name = self._expr.opts.objective_prefix + name

        if criteria:
            self.add_objective(name, criteria)

        return Score(self, name)

    def __call__(self, objective: str, criteria: str = None, prefixed=True):
        return self.objective(objective, criteria, prefixed)


@dataclass
class Score:
    ref: Scoreboard = field(repr=False)
    objective: str

    def __getitem__(self, scoreholder: str | tuple[str, ...]) -> ScoreSource | tuple[ScoreSource, ...]:
        if isinstance(scoreholder, str):
            return ScoreSource(scoreholder, self.objective, ctx=self.ref.ctx)

        return tuple(
            ScoreSource(holder, self.objective, ctx=self.ref.ctx)
            for holder in scoreholder
        )

    def __setitem__(self, scoreholder: str | tuple[str, ...], value: Any):
        target = self[scoreholder]

        scores = target if isinstance(target, tuple) else (target,)
        for score in scores:
            score.__rebind__(value)

    def __str__(self):
        return self.objective


@dataclass
class Data:
    ctx: Context = field(repr=False)

    def __post_init__(self):
        self._expr = self.ctx.inject(Expression)
        self.identifiers = identifier_generator(self.ctx)

    def __call__(self, target: str):
        """Guess target type and return a data source."""
        ...

    def storage(self, resource_location: str):
        return DataSource("storage", resource_location, ctx=self.ctx)

    def entity(self, entity: str):
        return DataSource("entity", entity, ctx=self.ctx)

    def block(self, position: str):
        return DataSource("block", position, ctx=self.ctx)

    def dummy(self, scale: int = 1, type: str = "int"):
        "Create a dummy data source in a storage."
        path = next(self.identifiers)
        target = self._expr.opts.temp_storage
        return DataSource("storage", target, Path(path), scale, type, ctx=self.ctx)

    def cast(self, value: Union[Source, Operation], type: str):
        source = self.dummy(type=type)
        if not isinstance(value, ExpressionNode):
            value = literal_types[type](value)
        self._expr.set(source, value)
        return replace(source, _nbt_type=None)
