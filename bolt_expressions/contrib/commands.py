from dataclasses import dataclass, replace
from typing import Any, Iterable, Tuple

from beet import Context
from beet.core.utils import required_field
from bolt import InterpolationParser, Runtime
from bolt.utils import internal
from mecha import (
    AstChildren,
    AstCommand,
    AstNode,
    CommandPrototype,
    CommandSpec,
    CommandTree,
    Mecha,
    MutatingReducer,
    rule,
)
from mecha.contrib.implicit_execute import ImplicitExecuteParser
from tokenstream import set_location

from bolt_expressions.sources import DataSource, ScoreSource, Source
from bolt_expressions.node import Expression

DEFAULT_PREFIX = "var"


def beet_default(ctx: Context):
    ctx.inject(commands)


def commands(ctx: Context):
    mc = ctx.inject(Mecha)
    runtime = ctx.inject(Runtime)

    mc.spec.parsers["command:argument:bolt_expressions:source"] = InterpolationParser(
        "source"
    )

    runtime.helpers["interpolate_source"] = SourceConverter(ctx=ctx)

    mc.transform.extend(SourceTransformer(mc=mc))

    prototypes = update_tree(mc.spec)

    update_implicit_execute(mc.spec, prototypes)


def update_tree(spec: CommandSpec):
    tree = spec.tree

    data_targets = (
        "minecraft:entity",
        "minecraft:block_pos",
        "minecraft:resource_location",
    )

    commands = spec.prototypes.keys()

    for command in commands:
        parsers = get_parsers(tree, command)
        scope = command.split(":")

        count = 0

        for i in range(0, len(parsers)):
            match parsers[: i + 1]:
                case [*_, "minecraft:score_holder", "minecraft:objective"]:
                    parent = tree.get(scope[: i - 1])
                    last_node = tree.get(scope[: i + 1])
                case [*_, None, target, "minecraft:nbt_path"] if target in data_targets:
                    parent = tree.get(scope[: i - 2])
                    last_node = tree.get(scope[: i + 1])
                case _:
                    continue

            prefix = DEFAULT_PREFIX
            name = f"sourceValue{count}"
            count += 1

            if prefix in parent.children:
                continue

            children = last_node.children

            end = CommandTree(
                type="argument",
                parser="bolt_expressions:source",
                properties={"prefix": prefix},
                redirect=last_node.redirect,
                executable=last_node.executable,
                subcommand=last_node.subcommand,
                children=None if children is None else dict(children),
            )
            parent.children[prefix] = CommandTree(type="literal", children={name: end})

    previous = set(spec.prototypes)

    spec.update()

    return set(spec.prototypes) - previous


def update_implicit_execute(spec: CommandSpec, prototypes: Iterable[CommandPrototype]):
    parser = spec.parsers["command"]
    while not isinstance(parser, ImplicitExecuteParser):
        parser = parser.parser

    keywords = {name.split(":", 2)[1] for name in parser.commands}

    commands = {
        name
        for name in prototypes
        if name.startswith("execute") and name.split(":", 2)[1] in keywords
    }
    shorthands = {
        name
        for name in prototypes
        if not name.startswith("execute") and name.split(":", 1)[0] not in keywords
    }

    parser.commands.update(commands)
    parser.shorthands.update(shorthands)


def get_parsers(tree: CommandTree, identifier: str):
    parsers = ()
    node = tree

    for name in identifier.split(":"):
        node = node.get(name)

        if node is None:
            break

        parsers += (node.parser,)

    return parsers


def get_child_argument_by_parser(node: CommandTree, parser: str):
    for name, child in node.children.items():
        if child.parser == parser:
            return name, child


def get_source_parsers(source: Source):
    if isinstance(source, ScoreSource):
        return ("score_holder", "objective")

    if isinstance(source, DataSource):
        if source._type == "entity":
            target = "entity"
        elif source._type == "storage":
            target = "resource_location"
        elif source._type == "block":
            target = "block_pos"
        else:
            target = None

        return (None, target, "nbt_path")


def get_source_values(source: Source):
    if isinstance(source, ScoreSource):
        return (source.scoreholder, source.objective)

    if isinstance(source, DataSource):
        return (source._type, source._target, str(source._path))


@dataclass(frozen=True)
class AstSourceNode(AstNode):
    value: Source = required_field()


@dataclass
class SourceConverter:
    ctx: Context | Expression

    @internal
    def __call__(self, obj: Any, node: AstNode):
        if isinstance(obj, AstNode):
            return set_location(obj, node.location, node.end_location)

        if isinstance(obj, Source):
            source = obj.evaluate()
        elif isinstance(obj, tuple) and len(obj) == 2:
            source = ScoreSource(*obj, ctx=self.ctx)
        elif isinstance(obj, tuple) and len(obj) == 3:
            source = DataSource(*obj, ctx=self.ctx)
        else:
            raise ValueError(
                f"Cannot interpolate source of type {type(obj)!r} '{obj}'."
            )

        return AstSourceNode(
            value=source, location=node.location, end_location=node.end_location
        )


@dataclass
class SourceTransformer(MutatingReducer):
    mc: Mecha = required_field()

    def get_argument_parent(
        self, command: AstCommand, arg_i: int
    ) -> Tuple[CommandTree, Tuple[str]]:
        spec = self.mc.spec

        prototype = spec.prototypes.get(command.identifier)
        prototype_arg = prototype.get_argument(arg_i)
        scope = prototype_arg.scope

        tree_arg = spec.tree.get(scope)

        properties = tree_arg.properties
        prefix = properties.get("prefix") if properties else None

        parent_scope = scope[:-1]
        offset = (prototype_arg.name,)

        if prefix and parent_scope[-1] == prefix:
            parent_scope = parent_scope[:-1]
            offset = (prefix, *offset)

        return spec.tree.get(parent_scope), offset

    @rule(AstCommand)
    def command(self, cmd_node: AstCommand):
        if not any(isinstance(n, AstSourceNode) for n in cmd_node.arguments):
            return cmd_node

        identifier = cmd_node.identifier
        arguments = []

        for i, cmd_arg in enumerate(cmd_node.arguments):
            if not isinstance(cmd_arg, AstSourceNode):
                arguments.append(cmd_arg)
                continue

            parent, parent_offset = self.get_argument_parent(cmd_node, i)

            source = cmd_arg.value

            parsers = get_source_parsers(source)
            values = get_source_values(source)

            arg_scope = []
            arg_parent = parent

            for parser, value in zip(parsers, values):
                if parser is None:
                    arg_scope.append(value)
                    arg_parent = arg_parent.get(value)
                    continue

                arg_name, arg_node = get_child_argument_by_parser(
                    arg_parent, parser if ":" in parser else f"minecraft:{parser}"
                )

                arg_ast = self.mc.parse(
                    value, using=parser, provide={"properties": arg_node.properties}
                )

                arguments.append(arg_ast)
                arg_scope.append(arg_name)

                arg_parent = arg_node

            identifier = identifier.replace(
                ":".join(parent_offset), ":".join(arg_scope), 1
            )

        arguments = AstChildren(arguments)

        return replace(cmd_node, identifier=identifier, arguments=arguments)
