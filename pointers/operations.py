from dataclasses import dataclass, field
from typing import Optional, Union, Dict, List
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


@dataclass(frozen=True)
class ScoreSource(ExpressionNode):
    scoreholder: str
    objective: str

    def __str__(self):
        return f"{self.scoreholder} {self.objective}"

@dataclass
class ExpressionContext:
    tempObjective: str
    constObjective: str
    outputSource: ScoreSource = None
    canUseOutput: bool = False
    constants: Dict[ScoreSource, int] = field(default_factory=dict)
    commands: List[str] = field(default_factory=list)
    prefix: str = '$temp'
    current_id: int = 0

    def __post_init__(self):
        self.canUseOutput = self.outputSource != None

    #def generateConstants(self):
    #    commands = Array.from(self.commands);
    #    self.commands = [];
    #    for source, value in self.constants.items():
    #        self.setLiteral(source, new Literal(value));
    #    output = self.commands;
    #    self.commands = commands;
    #    return output;

    def generateDummyName(self):
        self.current_id += 1
        return self.prefix + str(self.current_id)

    def createNamedSource(self, scoreholder: str, objective: str):
        return ScoreSource(scoreholder, objective)

    def createDummySource(self):
        name = self.generateDummyName()
        return self.createNamedSource(name, self.tempObjective)

    def createConstantSource(self, value: int):
        name = f"#{value}"
        source = self.createNamedSource(name, self.constObjective)
        #FIXME ScoreSource not hashable, might use a Map
        #self.constants[source] = value
        return source

    def createSource(self, reference: ScoreSource = None):
        if self.canUseOutput:
            self.canUseOutput = False # can use output only once
            # if provided a reference, init output source with reference's value
            # only if they're not equal (same scoreholder/objective)
            if reference != None and reference != self.outputSource:
                self.operateScore(self.outputSource, '=', reference)
            return self.outputSource
        # should create dummy source instead
        dummy = self.createDummySource()
        if reference != None: self.operateScore(dummy, '=', reference)
        return dummy

    def setLiteral(self, source: ScoreSource, value: int):
        cmd = f"scoreboard players set {source.scoreholder} {source.objective} {value}"
        self.commands.append(cmd)

    def addLiteral(self, source: ScoreSource, value: int):
        cmd = f"scoreboard players add {source.scoreholder} {source.objective} {value}"
        self.commands.append(cmd)

    def subtractLiteral(self, source: ScoreSource, value: int):
        cmd = f"scoreboard players remove {source.scoreholder} {source.objective} {value}"
        self.commands.append(cmd)

    def operateScore(self, target: ScoreSource, operation: str, source: ScoreSource):
        cmd = f"scoreboard players operation {target.scoreholder} {target.objective} {operation} {source.scoreholder} {source.objective}"
        self.commands.append(cmd)

    #def setScoreFromData(self, target: ScoreSource, source: DataSource):
    #    { target: tgt, objective: obj} = target
    #    cmd = f"execute store result score {tgt} {obj} run data get {source.type} {source.target} {source.path}"
    #    this.commands.append(cmd)
    #

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

    def resolveNode(self, term: ExpressionNode, exp: ExpressionContext, readOnly=False) -> ScoreSource:
        if isinstance(term, int):
            return exp.createConstantSource(term)
        if isinstance(term, ScoreSource):
            if readOnly: return term # doesnt need to create a dummy score
            return exp.createSource(term)
        return term.resolve(exp)

    def resolve(self, exp: ExpressionContext, operator: str) -> ScoreSource:
        result = self.resolveNode(self.former, exp)
        latter = self.resolveNode(self.latter, exp, True)
        exp.operateScore(result, operator, latter)
        return result

class Add(Operation):
    def resolve(self, exp: ExpressionContext):
        if isinstance(self.former, int):
            result = self.resolveNode(self.latter, exp)
            exp.addLiteral(result, self.former)
            return result
        if isinstance(self.latter, int):
            result = self.resolveNode(self.former, exp)
            exp.addLiteral(result, self.latter)
            return result
        return super().resolve(exp, '+=')

class Subtract(Operation):
    def resolve(self, exp: ExpressionContext):
        if isinstance(self.former, int):
            result = exp.createSource()
            latter = self.resolveNode(self.latter, exp, True)
            exp.setLiteral(result, self.former)
            exp.operateScore(result, '-=', latter)
            return result
        if isinstance(self.latter, int):
            result = self.resolveNode(self.former, exp)
            exp.subtractLiteral(result, self.latter)
            return result
        return super().resolve(exp, '-=')

class Multiply(Operation):
    def resolve(self, exp: ExpressionContext):
        if isinstance(self.former, int):
            result = self.resolveNode(self.latter, exp)
            former = exp.createConstantSource(self.former)
            exp.operateScore(result, '*=', former)
            return result
        return super().resolve(exp, '*=')
class Divide(Operation):
    def resolve(self, exp: ExpressionContext):
        if isinstance(self.former, int):
            result = exp.createSource()
            latter = self.resolveNode(self.latter, exp, True)
            exp.setLiteral(result, self.former)
            exp.operateScore(result, '/=', latter)
            return result
        return super().resolve(exp, '/=')
class Modulus(Operation):
    def resolve(self, exp: ExpressionContext):
        if isinstance(self.former, int):
            result = exp.createSource()
            latter = self.resolveNode(self.latter, exp, True)
            exp.setLiteral(result, self.former)
            exp.operateScore(result, '%=', latter)
            return result
        return super().resolve(exp, '/=')


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


    def __setitem__(self, scoreholder: str, value: Union[ExpressionNode, GenericValue]):
        print(f"Setting {self[scoreholder]} to {value}")
        output = self[scoreholder]
        exp = ExpressionContext('temp', 'const', output)
        if isinstance(value, Operation): value.resolve(exp)
        elif isinstance(value, int): exp.setLiteral(output, value)
        elif isinstance(value, ScoreSource): exp.operateScore(output, '=', value)
        else: raise ValueError(f"Invalid expression argument of type {type(value)}.")
        print("\nGENERATED:")
        for cmd in exp.commands:
            print(cmd)

# myself = Score("@s", "temp")
# value = Score("#value", "temp")
# myself += value * 2 + (myself * 2)