from dataclasses import dataclass, field
from typing import Union
from beet import Context

GenericValue = Union["Score", int]

@dataclass
class ExpressionNode:    
    def __add__(self, other: "ExpressionNode"):
        print(f"Adding {self} to {other}")
        return Add(self, other)
        
    def __sub__(self, other: "ExpressionNode"):
        print(f"Subtracting {self} to {other}")
        return Subtract(self, other)
        
    def __mul__(self, other: "ExpressionNode"):
        print(f"Multiplying {self} to {other}")
        return Multiply(self, other)
        
    def __truediv__(self, other: "ExpressionNode"):
        print(f"Dividing {self} to {other}")
        return Divide(self, other)
        
    def __mod__(self, other: "ExpressionNode"):
        print(f"Modulus {self} to {other}")
        return Modulus(self, other)


@dataclass
class ScoreSource(ExpressionNode):
    scoreholder: str
    objective: str

@dataclass
class Operation(ExpressionNode):
    former: GenericValue
    latter: GenericValue


class Add(Operation):
    pass

class Subtract(Operation):
    pass

class Multiply(Operation):
    pass

class Divide(Operation):
    pass

class Modulus(Operation):
    pass


@dataclass
class Score:
    ctx: Context
    objective: str

    def __getitem__(self, scoreholder: str) -> ExpressionNode:
        return ScoreSource(scoreholder, self.objective)
    
    def __setitem__(self, scoreholder: str, value: Union[ExpressionNode, GenericValue]):
        ...


# myself = Score("@s", "temp")
# value = Score("#value", "temp")
# myself += value * 2 + (myself * 2)