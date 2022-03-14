from dataclasses import InitVar, dataclass
from functools import cached_property
from typing import Any, Optional, Tuple, TypeVar, Union

from beet import Context

from mecha import Mecha
from mecha.contrib.bolt import Runtime

from .operations import Score

# ValueHolder = Union["Score", "Storage"]
# GenericValue = Union[int, ValueHolder]

# def _operation(left: "Score", operation: str, right: "Score") -> str:
#     return f"scoreboard players operation {left} {operation} {right}"

# def _raw(score: "Score", operation: str, val: int) -> str:
#     return f"scoreboard players {operation} {score} {val}"

# def _store(score: "Score", storage: "Storage") -> str:
#     return f"execute store result score {score} run data get storage {val}"

# def _temp(self, storage: "Storage") -> Tuple[str, "Score"]:
#     temp = Score("$storage.score.operation", "rx.temp")
#     cmd = f"execute store result score {temp} run data get storage {storage}"
#     return cmd, temp

@dataclass
class Scoreboard:
    ctx: Context
    
    @cached_property
    def _runtime(self) -> Runtime:
        return self.ctx.inject(Runtime)

    @cached_property
    def _mc(self) -> Mecha:
        return self.ctx.inject(Mecha)
        
    def _inject_command(self, cmd: str):
        self._runtime.commands.append(
            self._mc.parse(cmd, using="command")
        )

    def __call__(self, scoreholder):
        return Score(self.ctx, scoreholder)
    
    def test(self):
        print(self.ctx)


# @dataclass
# class Scoreholder:
#     scoreboard: Scoreboard
#     scoreholder: str
#     objective: str

#     def set(self, val: GenericValue):
#         if type(val) is int:
#             return _raw(self, "set", val)
#         elif type(val) is Score:
#             return _operation(self, "=", val)
        
#         return _store(self, val)
    
#     def __add__(self, other: GenericValue) -> str:
#         if type(other) is Score:
#             return _operation(self._value, "+=", other)
        
#         return _raw(self, "add", other)
    
#     def __sub__(self, other: GenericValue) -> str:
#         if type(other) is Score:
#             return _operation(self._value, "-=", other)
#         elif type(other) is Storage:
#             cmd, temp = _temp(other)
        
#         return _raw(self, "remove", other)
    
#     def __mul__(self, other: GenericValue) -> str:
#         if type(other) is Score:
#             return _operation(self._value, "*=", other)
#         elif type(other) is Storage:
#             cmd, temp = _temp(other)
#             return "\n".join((
#                 cmd,
#                 self.__mul__(temp)
#             ))
        
#         raise NotImplementedError
        
#     def __div__(self, other: ValueHolder) -> str:
#         if type(other) is Score:
#             return _operation(self._value, "/=", other)

#     def __str__(self):
#         return f"{self.scoreholder} {self.objective}"


# @dataclass
# class Storage:
#     namespace: str
#     nbt: str  # ??

#     def __str__(self):
#         return f"{self.namespace} {self.nbt}"
    