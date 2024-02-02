from dataclasses import dataclass, field
from typing import Any, overload

from beet import Context
from bolt.utils import internal

from .typing import NbtType, literal_types
from .node import Expression
from .sources import (
    DataSource,
    ScoreSource,
)


__all__ = [
    "Scoreboard",
    "Objective",
    "Data",
]


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

    expr: Expression

    constants: set[int]
    objectives: set[str]
    added_objectives: set[str]

    def __init__(self, ctx: Context | Expression):
        if isinstance(ctx, Context):
            self.expr = ctx.inject(Expression)
        else:
            self.expr = ctx

        opts = self.expr.opts

        self.constants = set()
        self.objectives = {opts.const_objective, opts.temp_objective}
        self.added_objectives = set()

    def add_objective(self, name: str, criteria: str = "dummy"):
        if name not in self.added_objectives:
            self.added_objectives.add(name)

            self.expr.init_commands.insert(
                0, f"scoreboard objectives add {name} {criteria}"
            )

    def add_constant(self, value: int):
        holder, obj = self.expr.const_score(value)

        if not value in self.constants:
            self.constants.add(value)
            self.expr.init_commands.append(
                f"scoreboard players set {holder} {obj} {value}"
            )

    def objective(
        self, name: str, criteria: str | None = None, prefixed: bool = True
    ) -> "Objective":
        """
        Get an Objective instance and add objective to init function if provided criteria.
        """

        if prefixed:
            name = self.expr.opts.objective_prefix + name

        if criteria:
            self.add_objective(name, criteria)

        return Objective(name, ctx=self.expr)

    __call__ = objective

    def score(self, scoreholder: str, objective: str) -> ScoreSource:
        return ScoreSource(scoreholder, objective, ctx=self.expr)


@dataclass
class Objective:
    name: str
    ctx: Context | Expression = field(kw_only=True)

    @overload
    def __getitem__(self, scoreholder: str) -> ScoreSource:
        ...

    @overload
    def __getitem__(self, scoreholder: tuple[str, ...]) -> tuple[ScoreSource, ...]:
        ...

    def __getitem__(
        self, scoreholder: str | tuple[str, ...]
    ) -> ScoreSource | tuple[ScoreSource, ...]:
        if isinstance(scoreholder, str):
            return ScoreSource(scoreholder, self.name, ctx=self.ctx)

        return tuple(
            ScoreSource(holder, self.name, ctx=self.ctx) for holder in scoreholder
        )

    @internal
    def __setitem__(self, scoreholder: str | tuple[str, ...], value: Any):
        target = self[scoreholder]

        scores = target if isinstance(target, tuple) else (target,)
        for score in scores:
            score.__rebind__(value)

    def __str__(self):
        return self.name


class Data:
    expr: Expression

    def __init__(self, ctx: Context | Expression):
        if isinstance(ctx, Context):
            self.expr = ctx.inject(Expression)
        else:
            self.expr = ctx

    def __call__(self, target: str):
        """Guess target type and return a data source."""
        ...

    def storage(self, resource_location: str):
        return DataSource("storage", resource_location, ctx=self.expr)

    def entity(self, entity: str):
        return DataSource("entity", entity, ctx=self.expr)

    def block(self, position: str):
        return DataSource("block", position, ctx=self.expr)

    def dummy(self, type: NbtType | str = Any):
        "Create a dummy data source in a storage."

        if isinstance(type, str):
            type = literal_types[type]

        target_type, target, path = self.expr.temp_data()
        return DataSource(target_type, target, path, ctx=self.expr)[type]

    def cast(self, value: Any, nbt_type: NbtType | str):
        if isinstance(nbt_type, str):
            nbt_type = literal_types[nbt_type]

        source = self.dummy(nbt_type)
        source.__rebind__(value)

        return source
