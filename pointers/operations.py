from dataclasses import dataclass
from typing import Iterable, List, Union

from itertools import count

infinite = count()

@dataclass(frozen=True)
class ExpressionNode:
    def __add__(self, other: "ExpressionNode"):
        # print(f"Adding {self} by {other}")
        return Add.create(self, other)
    
    def __radd__(self, other: "ExpressionNode"):
        # print(f"Adding {self} by {other}")
        return Add.create(other, self)

    def __sub__(self, other: "ExpressionNode"):
        # print(f"Subtracting {self} by {other}")
        return Subtract.create(self, other)

    def __rsub__(self, other: "ExpressionNode"):
        # print(f"Subtracting {self} by {other}")
        return Subtract.create(other, self)

    def __mul__(self, other: "ExpressionNode"):
        # print(f"Multiplying {self} by {other}")
        return Multiply.create(self, other)
    
    def __rmul__(self, other: "ExpressionNode"):
        # print(f"Multiplying {self} by {other}")
        return Multiply.create(other, self)

    def __truediv__(self, other: "ExpressionNode"):
        # print(f"Dividing {self} by {other}")
        return Divide.create(self, other)

    def __rtruediv__(self, other: "ExpressionNode"):
        # print(f"Dividing {self} by {other}")
        return Divide.create(other, self)
    
    def __floordiv__(self, other: "ExpressionNode"):
        return Divide.create(other, self)
    
    def __rfloordiv__(self, other: "ExpressionNode"):
        return Divide.create(other, self)

    def __mod__(self, other: "ExpressionNode"):
        # print(f"Modulus {self} by {other}")
        return Modulus.create(self, other)

    def __rmod__(self, other: "ExpressionNode"):
        # print(f"Modulus {self} by {other}")
        return Modulus.create(other, self)
    
    def unroll(self) -> Iterable["Operation"]:
        yield self

@dataclass(frozen=True)
class ScoreSource(ExpressionNode):
    scoreholder: str
    objective: str

    def __str__(self):
        return f'{self.scoreholder} {self.objective}'
    
    def __repr__(self):
        return f'"{str(self)}"'

@dataclass(frozen=True)
class Operation(ExpressionNode):
    former: Union["Operation", ScoreSource]
    latter: Union["Operation", ScoreSource, int]

    @classmethod
    def create(cls, former, latter):
        """Factory method to create new operations"""
        
        # TODO: int is hardcoded, we need to generate this stuff
        if type(former) is float: former = int(former)
        if type(latter) is float: latter = int(latter)
        if type(former) is int:
            former = ScoreSource(f"${former}", "int")
        if type(latter) is int:
            latter = ScoreSource(f"${latter}", "int")
        
        return cls(former, latter)
        

    def unroll(self) -> Iterable["Operation"]:
        print(f"{type(self).__name__}")
        print(self)
        
        former_nodes = list(self.former.unroll())
        latter_nodes = list(self.latter.unroll())

        temp_var = ScoreSource("temp", f"$i{next(infinite)}")

        yield from former_nodes[:-1]
        yield from latter_nodes[:-1]

        if type(self) is not Set:
            yield Set.create(temp_var, former_nodes.pop())
            yield self.__class__.create(temp_var, latter_nodes.pop())
            yield temp_var
        else:
            yield Set.create(former_nodes.pop(), latter_nodes.pop())


    # def resolve_node(
    #     self, term: ExpressionNode, exp: ExpressionContext, read_only=False
    # ) -> ScoreSource:
    #     if isinstance(term, int):
    #         return exp.create_constant_source(term)
    #     if isinstance(term, ScoreSource):
    #         if read_only:
    #             return term  # doesnt need to create a dummy score
    #         return exp.create_source(term)
    #     return term.resolve(exp)

    # def resolve(self, exp: ExpressionContext, operator: str) -> ScoreSource:
    #     result = self.resolve_node(self.former, exp)
    #     latter = self.resolve_node(self.latter, exp, True)
    #     exp.operate_score(result, operator, latter)
    #     return result


class Set(Operation):
    def resolve(self, exp: "ExpressionContext"):
        if isinstance(self.former, int):
            result = self.resolve_node(self.latter, exp)
            exp.add_literal(result, self.former)
            return result
        if isinstance(self.latter, int):
            result = self.resolve_node(self.former, exp)
            exp.add_literal(result, self.latter)
            return result
        return super().resolve(exp, "=")

class Add(Operation):
    def resolve(self, exp: "ExpressionContext"):
        if isinstance(self.former, int):
            result = self.resolve_node(self.latter, exp)
            exp.add_literal(result, self.former)
            return result
        if isinstance(self.latter, int):
            result = self.resolve_node(self.former, exp)
            exp.add_literal(result, self.latter)
            return result
        return super().resolve(exp, "+=")


class Subtract(Operation):
    def resolve(self, exp: "ExpressionContext"):
        if isinstance(self.former, int):
            result = exp.create_source()
            latter = self.resolve_node(self.latter, exp, True)
            exp.set_literal(result, self.former)
            exp.operate_score(result, "-=", latter)
            return result
        if isinstance(self.latter, int):
            result = self.resolve_node(self.former, exp)
            exp.subtract_literal(result, self.latter)
            return result
        return super().resolve(exp, "-=")


class Multiply(Operation):
    def resolve(self, exp: "ExpressionContext"):
        if isinstance(self.former, int):
            result = self.resolve_node(self.latter, exp)
            former = exp.create_constant_source(self.former)
            exp.operate_score(result, "*=", former)
            return result
        return super().resolve(exp, "*=")


class Divide(Operation):
    def resolve(self, exp: "ExpressionContext"):
        if isinstance(self.former, int):
            result = exp.create_source()
            latter = self.resolve_node(self.latter, exp, True)
            exp.set_literal(result, self.former)
            exp.operate_score(result, "/=", latter)
            return result
        return super().resolve(exp, "/=")


class Modulus(Operation):
    def resolve(self, exp: "ExpressionContext"):
        if isinstance(self.former, int):
            result = exp.create_source()
            latter = self.resolve_node(self.latter, exp, True)
            exp.set_literal(result, self.former)
            exp.operate_score(result, "%=", latter)
            return result
        return super().resolve(exp, "/=")



# myself = Score("@s", "temp")
# value = Score("#value", "temp")
# myself += value * 2 + (myself * 2)
