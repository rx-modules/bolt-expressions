from dataclasses import dataclass, field
from typing import Optional, Union, List
from beet import Context

GenericValue = Union["ScoreSource", int]

@dataclass
class ExpressionNode:    
    def __add__(self, other: "ExpressionNode"):
        # print(f"Adding {self} by {other}")
        return Add(self, other)
        
    def __sub__(self, other: "ExpressionNode"):
        # print(f"Subtracting {self} by {other}")
        return Subtract(self, other)
        
    def __mul__(self, other: "ExpressionNode"):
        # print(f"Multiplying {self} by {other}")
        return Multiply(self, other)
        
    def __truediv__(self, other: "ExpressionNode"):
        # print(f"Dividing {self} by {other}")
        return Divide(self, other)
        
    def __mod__(self, other: "ExpressionNode"):
        # print(f"Modulus {self} by {other}")
        return Modulus(self, other)


@dataclass
class ScoreSource(ExpressionNode):
    scoreholder: str
    objective: str

    def __str__(self):
        return f"{self.scoreholder} {self.objective}"

@dataclass
class Operation(ExpressionNode):
    former: Union["Operation", ScoreSource]
    latter: Union["Operation", GenericValue]

    operation: str = field(default="scoreboard players operation {former} {operand} {latter}", repr=False)
    
    def resolve(self):
        return self.operation.format(former=self.former, operand=self.operand, latter=self.latter)
    
    def __post_init__(self):
        # TODO: add score to init file
        # TODO: use generic integer obj / something from config
        if type(self.latter) is int:
            self.latter = ScoreSource(f"${self.latter}", "rx.int")

class Set(Operation):
    operand: str = "="

class Add(Operation):
    operand: str = "+="

class Subtract(Operation):
    operand: str = "-="

class Multiply(Operation):
    operand: str = "*="

class Divide(Operation):
    operand: str = "/="

class Modulus(Operation):
    operand: str = "%="


@dataclass
class Score:
    ctx: Context = field(repr=False)
    objective: str

    def __getitem__(self, scoreholder: str) -> ExpressionNode:
        return ScoreSource(scoreholder, self.objective)
    
    def __setitem__(self, scoreholder: str, value: Union[Operation, GenericValue]):
        # print(f"Setting {self} to {value}")
        
        cmds = self.resolve(Set(self.__getitem__(scoreholder), value))
        print('\n'.join(cmds))
        print()

    def resolve(self, root: Union[ExpressionNode, int]) -> List[str]:
        if isinstance(root, Operation):
            yield from self.resolve(root.former)
            yield from self.resolve(root.latter)
            yield root.resolve()



# myself = Score("@s", "temp")
# value = Score("#value", "temp")
# myself += value * 2 + (myself * 2)