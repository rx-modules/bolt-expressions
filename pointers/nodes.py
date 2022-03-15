from dataclasses import dataclass, field
from typing import Dict, List, Optional, Union

from beet import Context

GenericValue = Union["ScoreSource", int]

from .operations import Add, Subtract, Multiply, Divide, Modulus




# @dataclass
# class ExpressionContext:
#     temp_objective: str
#     const_objective: str
#     output_source: ScoreSource = None
#     can_use_output: bool = False
#     constants: Dict[ScoreSource, int] = field(default_factory=dict)
#     commands: List[str] = field(default_factory=list)
#     prefix: str = "$temp"
#     current_id: int = 0

#     def __post_init__(self):
#         self.can_use_output = self.output_source != None

#     # def generate_constants(self):
#     #    commands = Array.from(self.commands);
#     #    self.commands = [];
#     #    for source, value in self.constants.items():
#     #        self.setLiteral(source, new Literal(value));
#     #    output = self.commands;
#     #    self.commands = commands;
#     #    return output;

#     def generate_dummy_name(self):
#         self.current_id += 1
#         return self.prefix + str(self.current_id)

#     def create_named_source(self, scoreholder: str, objective: str):
#         return ScoreSource(scoreholder, objective)

#     def create_dummy_source(self):
#         name = self.generate_dummy_name()
#         return self.create_named_source(name, self.temp_objective)

#     def create_constant_source(self, value: int):
#         name = f"#{value}"
#         source = self.create_named_source(name, self.const_objective)
#         # FIXME ScoreSource not hashable, might use a Map
#         # self.constants[source] = value
#         return source

#     def create_source(self, reference: ScoreSource = None):
#         if self.can_use_output:
#             self.can_use_output = False  # can use output only once
#             # if provided a reference, init output source with reference's value
#             # only if they're not equal (same scoreholder/objective)
#             if reference != None and reference != self.output_source:
#                 self.operate_score(self.output_source, "=", reference)
#             return self.output_source
#         # should create dummy source instead
#         dummy = self.create_dummy_source()
#         if reference != None:
#             self.operate_score(dummy, "=", reference)
#         return dummy

#     def set_literal(self, source: ScoreSource, value: int):
#         cmd = f"scoreboard players set {source.scoreholder} {source.objective} {value}"
#         self.commands.append(cmd)

#     def add_literal(self, source: ScoreSource, value: int):
#         cmd = f"scoreboard players add {source.scoreholder} {source.objective} {value}"
#         self.commands.append(cmd)

#     def subtract_literal(self, source: ScoreSource, value: int):
#         cmd = (
#             f"scoreboard players remove {source.scoreholder} {source.objective} {value}"
#         )
#         self.commands.append(cmd)

#     def operate_score(self, target: ScoreSource, operation: str, source: ScoreSource):
#         cmd = f"scoreboard players operation {target.scoreholder} {target.objective} {operation} {source.scoreholder} {source.objective}"
#         self.commands.append(cmd)

#     # def set_score_from_data(self, target: ScoreSource, source: DataSource):
#     #    { target: tgt, objective: obj} = target
#     #    cmd = f"execute store result score {tgt} {obj} run data get {source.type} {source.target} {source.path}"
#     #    this.commands.append(cmd)
#     #