from typing import Dict

from beet import Context
from bolt import Runtime

__all__ = [
    "identifier_generator",
]


def identifier_generator(ctx: Context):
    runtime = ctx.inject(Runtime)
    incr: Dict[str, int] = {}
    while True:
        path = runtime.modules.current_path
        incr[path] = incr.setdefault(path, -1) + 1
        yield ctx.generate.format(f"{{hash}}_{incr[path]}", path)
