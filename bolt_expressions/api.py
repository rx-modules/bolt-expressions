from dataclasses import dataclass, field, replace
from functools import cached_property
from typing import Iterable, List, Union

from beet import Context, Function, FunctionTag
from bolt import Runtime
from mecha import AstChildren, AstCommand, AstNode, AstRoot, Mecha
from pydantic import BaseModel

from . import resolver
from .ast import ExecuteTransformer, ConstantScoreChecker
from .literals import literal_types
from .node import ExpressionMethods, ExpressionNode
from .operations import (
    Append,
    GenericValue,
    Insert,
    Merge,
    MergeRoot,
    Operation,
    Prepend,
    Set,
    wrapped_max,
    wrapped_min,
)
from . import conditions
from .optimizer import Optimizer
from .sources import (
    ConstantScoreSource,
    DataSource,
    ScoreSource,
    Source,
    TempScoreSource,
)
from .utils import identifier_generator, insert_nested_commands

# from rich import print
# from rich.pretty import pprint


class ExpressionOptions(BaseModel):
    """Bolt Expressions Options"""

    temp_objective: str = "bolt.expr.temp"
    const_objective: str = "bolt.expr.const"
    temp_storage: str = "bolt.expr:temp"
    init_path: str = "init_expressions"
    objective_prefix: str = ""


@dataclass
class Expression:
    ctx: Context = field(repr=False)
    activated: bool = False
    called_init: bool = False
    init_commands: List[str] = field(default_factory=list)
    methods: ExpressionMethods = field(init=False)

    def __post_init__(self):
        if not self.activated:
            self.opts = self.ctx.validate("bolt_expressions", ExpressionOptions)
            self._runtime.expose("min", wrapped_min)
            self._runtime.expose("max", wrapped_max)
            self._mc.transform.extend(ExecuteTransformer())
            self.activated = True

        TempScoreSource.objective = self.opts.temp_objective
        ConstantScoreSource.objective = self.opts.const_objective
        self.methods = ExpressionMethods()
        self.methods.add(ExpressionNode, _resolve_branch=self.resolve_branch)
        self.init_commands.append(
            f"scoreboard objectives add {self.opts.temp_objective} dummy"
        )
        self.init_commands.append(
            f"scoreboard objectives add {self.opts.const_objective} dummy"
        )

    @cached_property
    def _runtime(self) -> Runtime:
        return self.ctx.inject(Runtime)

    @cached_property
    def _mc(self) -> Mecha:
        return self.ctx.inject(Mecha)

    def _inject_command(self, cmd: str):
        self.inject_node(self._mc.parse(cmd, using="command"))

    def inject_node(self, node: AstNode):
        self._runtime.commands.append(node)

    def resolve(self, nodes: Operation | Iterable[Operation]):
        # pprint(nodes)
        if isinstance(nodes, Operation):
            nodes = list(nodes.unroll())
        # pprint(nodes)
        nodes = list(Optimizer.optimize(nodes))
        # pprint(nodes)
        cmds = list(resolver.resolve(nodes))
        # pprint(cmds, expand_all=True)
        for cmd in cmds:
            self._inject_command(cmd)

    def resolve_branch(self, node: ExpressionNode):
        *nodes, result = node.unroll()

        if nodes:
            self.resolve(nodes)

        with self._runtime.scope() as commands:
            yield True

        condition = resolver.generate("istrue", result)
        parsed = self._mc.parse(condition, using="command")
        root = AstRoot(commands=AstChildren(commands))
        commands = AstCommand(
            identifier="execute:commands", arguments=AstChildren((root,))
        )
        output = insert_nested_commands(parsed, commands)
        self.inject_node(output)

    def set(self, source: Source, value: GenericValue):
        self.resolve(Set.create(source, value))

    def init(self):
        """Injects a function which creates `ConstantSource` fakeplayers"""
        path = self.ctx.generate.path(self.opts.init_path)
        self._inject_command(f"function {path}")
        self.called_init = True

    def generate_init(self):
        self.ctx.generate(
            self.opts.init_path,
            Function(
                self.init_commands,
                prepend_tags=["minecraft:load"] if not self.called_init else None,
            ),
        )


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
    constants: set[int] = field(default_factory=set)

    def __post_init__(self):
        self._expr = self.ctx.inject(Expression)
        self._expr._mc.check.extend(
            ConstantScoreChecker(
                objective=self._expr.opts.const_objective, callback=self.add_constant
            )
        )
        self._expr.methods.add(
            ScoreSource, rebind=self.set_score, reset=self.reset, enable=self.enable
        )

    def add_constant(self, node: ConstantScoreSource):
        if not node.value in self.constants:
            self.constants.add(node.value)
            self._expr.init_commands.append(
                f"scoreboard players set {node} {node.value}"
            )

    def set_score(self, score: ScoreSource, value: GenericValue):
        return self._expr.set(score, value)

    def objective(self, name: str, prefixed=True):
        """Get a Score instance through the Scoreboard API"""
        if prefixed:
            name = self._expr.opts.objective_prefix + name
        return Score(self, name)

    def __call__(self, objective: str, *holders: List[str], prefixed_obj=True):
        obj = self.objective(objective, prefixed_obj)
        if len(holders):
            return obj[holders]
        return obj

    def reset(self, source: ScoreSource):
        cmd = resolver.generate("reset:score", source)
        self._expr._inject_command(cmd)

    def enable(self, source: ScoreSource):
        cmd = resolver.generate("enable:score", source)
        self._expr._inject_command(cmd)


@dataclass
class Score:
    ref: Scoreboard = field(repr=False)
    objective: str

    def __getitem__(self, scoreholder: Union[str, List[str]]) -> ScoreSource:
        methods = self.ref._expr.methods
        if type(scoreholder) is str:
            return ScoreSource.create(scoreholder, self.objective, methods=methods)
        return [
            ScoreSource.create(holder, self.objective, methods=methods)
            for holder in scoreholder
        ]

    def __setitem__(self, scoreholder: str, value: Operation):
        self.ref.set_score(self[scoreholder], value)

    def __str__(self):
        return self.objective


@dataclass
class Data:
    ctx: Context = field(repr=False)

    def __post_init__(self):
        self._expr = self.ctx.inject(Expression)
        self.identifiers = identifier_generator(self.ctx)
        self._expr.methods.add(
            DataSource,
            rebind=self.set_data,
            remove=self.remove,
            append=self.append,
            prepend=self.prepend,
            insert=self.insert,
            merge=self.merge,
        )

    def __call__(self, target: str):
        """Guess target type and return a data source."""
        ...

    def set_data(self, source: DataSource, value: GenericValue):
        return self._expr.set(source, value)

    def storage(self, resource_location: str):
        return DataSource.create("storage", resource_location, methods=self._expr.methods)

    def entity(self, entity: str):
        return DataSource.create("entity", entity, methods=self._expr.methods)

    def block(self, position: str):
        return DataSource.create("block", position, methods=self._expr.methods)

    def dummy(self, scale: int = 1, type: str = "int"):
        "Create a dummy data source in a storage."
        path = next(self.identifiers)
        target = self._expr.opts.temp_storage
        return DataSource.create(
            "storage", target, path, scale, type, methods=self._expr.methods
        )

    def cast(self, value: Union[Source, Operation], type: str):
        source = self.dummy(type=type)
        if not isinstance(value, ExpressionNode):
            value = literal_types[type](value)
        self._expr.set(source, value)
        return replace(source, _nbt_type=None)

    def remove(self, source: DataSource, value: Union[str, int] = None):
        node = source if value is None else source[value]
        if not len(node._path):
            raise ValueError(
                f'Cannot remove the root of {node._type} "{node._target}".'
            )
        cmd = resolver.generate("remove:data", value=node)
        self._expr._inject_command(cmd)

    def append(self, source: DataSource, value: GenericValue):
        self._expr.resolve(Append.create(source, value))

    def prepend(self, source: DataSource, value: GenericValue):
        self._expr.resolve(Prepend.create(source, value))

    def insert(self, source: DataSource, index: int, value: GenericValue):
        self._expr.resolve(Insert.create(source, value, index=index))

    def merge(self, source: DataSource, value: GenericValue):
        Operation = Merge if len(source._path) else MergeRoot
        self._expr.resolve(Operation.create(source, value))
