from typing import Dict
from dataclasses import replace

from beet import Context
from bolt import Runtime
from mecha import AstCommand, AstChildren


def identifier_generator(ctx: Context):
    runtime = ctx.inject(Runtime)
    incr: Dict[str, int] = {}
    while True:
        path = runtime.modules.current_path
        incr[path] = incr.setdefault(path, -1) + 1
        yield ctx.generate.format(f"{{hash}}_{incr[path]}", path)


def insert_nested_commands(execute: AstCommand, commands: AstCommand):
    """Inserts nested commands to the end of an execute command."""

    if not isinstance(execute.arguments[-1], AstCommand):
        arguments = AstChildren((*execute.arguments, commands))
        identifier = execute.identifier + ":subcommand"
        return replace(execute, identifier=identifier, arguments=arguments)

    inserted = insert_nested_commands(execute.arguments[-1], commands)
    arguments = AstChildren((*execute.arguments[:-1], inserted))
    return replace(execute, arguments=arguments)
