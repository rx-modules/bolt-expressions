import logging
from bisect import bisect
from dataclasses import dataclass
from functools import cached_property
from inspect import stack
from os import linesep
from typing import Literal

from beet import Context
from bolt import Runtime
from mecha import Diagnostic, Mecha
from tokenstream import SourceLocation, set_location


def get_line_location(input: str, lineno: int):
    i = 0

    for _ in range(lineno - 1):
        i = input.find(linesep, i)

        if i < 0:
            return -1

        i += len(linesep)

    return i


def get_line_end_location(input: str, lineno: int):
    i = get_line_location(input, lineno + 1)

    if i < 0:
        return len(input)

    return i - len(linesep)


LogLevel = Literal["info", "warn", "error"]


@dataclass
class BoltLogger:
    """Emits helpful Mecha diagnostics for Bolt libraries written in Python."""

    ctx: Context
    name: str = "bolt_expressions"

    @cached_property
    def logger(self):
        return logging.getLogger(self.name)

    @cached_property
    def _mc(self) -> Mecha:
        return self.ctx.inject(Mecha)

    @cached_property
    def _runtime(self) -> Runtime:
        return self.ctx.inject(Runtime)

    def __call__(self, level: LogLevel, message: str):
        module_path = self._runtime.modules.current_path
        lineno = None

        for frameinfo in stack():
            name = frameinfo.frame.f_globals["__name__"]

            if module_path == name:
                lineno = frameinfo.lineno
                break

        module = self._runtime.modules[module_path]
        file = self._mc.database.index[module_path]
        unit = self._mc.database[file]

        n1, n2 = module.namespace.get("_bolt_lineno", ([], []))
        module_lineno = n2[bisect(n1, lineno) - 1]

        source = unit.source or ""
        pos = get_line_location(source, module_lineno)
        end_pos = get_line_end_location(source, module_lineno)

        location = SourceLocation(pos, module_lineno, 1)
        end_location = SourceLocation(end_pos, module_lineno, end_pos - pos + 1)

        exc = set_location(
            Diagnostic(level, message, file=file, rule=self.name),
            location,
            end_location,
        )
        unit.diagnostics.add(exc)
