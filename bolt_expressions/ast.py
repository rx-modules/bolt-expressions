from dataclasses import dataclass
from mecha import MutatingReducer, rule, AstCommand


@dataclass
class ExecuteTransformer(MutatingReducer):
    @rule(AstCommand, identifier="execute:run:subcommand")
    def strip_run_execute(self, node: AstCommand):
        if isinstance(command := node.arguments[0], AstCommand):
            if command.identifier == "execute:subcommand":
                return command.arguments[0]
        return node
