import sys

from LLVMGenerator import LLVMGenerator

from generated.GenshinLangParser import GenshinLangParser
from generated.GenshinLangListener import GenshinLangListener

variables = {}

class Value:
    def __init__(self, type="undefined", value="undefined"):
        self.type = type
        self.value = value

class GenshinASTBuilder(GenshinLangListener):
    def __init__(self):
        self.generator = LLVMGenerator()
        self.ast = []

    def exitVariable(self, ctx:GenshinLangParser.VariableContext):
        varType = ctx.IDENTIFIER().getText()
        ident = ctx.IDENTIFIER().getText()

        if ident in variables:
                print("Tak zdefiniowana zmienna już isnieje!", file=sys.stderr)
                sys.exit(-1)
        
        variables[ident] = Value()

    def exitVariableAssign(self, ctx:GenshinLangParser.VariableAssignContext):
        varType = ""
        ident = ctx.IDENTIFIER().getText()
        if ctx.TYPE():
            varType = ctx.TYPE().getText()
            if ident in variables:
                print("Tak zdefiniowana zmienna już isnieje!", file=sys.stderr)
                sys.exit(-1)
        
        self.ast.append(ctx)

        element = ctx.elemToAssign().getText()
        variables[ident] = Value(varType, element)

    def exitElemToAssign(self, ctx:GenshinLangParser.ElemToAssignContext):
        self.ast.append(ctx)
        return ctx.expression()

    def exitExpression(self, ctx:GenshinLangParser.ExpressionContext):
        self.ast.append(ctx)
        value = self.exitTerm(ctx.term(0))
        
        children = list(ctx.getChildren())
        for i in range(1, len(ctx.term())):
            operator = children[2*i-1].getText()
            value2 = self.exitTerm(ctx.term(i))
            
            if operator == "+":
                value += value2
            elif operator == "-":
                value -= value2
        
        return value

    def exitTerm(self, ctx:GenshinLangParser.TermContext):
        value = self.exitFactor(ctx.factor(0))
        
        children = list(ctx.getChildren())
        for i in range(1, len(ctx.factor())):
            operator = children[2*i-1].getText()
            value2 = self.exitFactor(ctx.factor(i))
            
            if operator == "*":
                value *= value2
            elif operator == "/":
                value /= value2
        
        return value

    def exitFactor(self, ctx:GenshinLangParser.FactorContext):
        self.ast.append(ctx)
        if ctx.NUMBER():
            return float(ctx.NUMBER().getText())
        if ctx.IDENTIFIER():
            ident = ctx.IDENTIFIER().getText()
            if ident in variables:
                return float(variables[ident].value)

    def exitPrintStat(self, ctx:GenshinLangParser.PrintStatContext):
        self.ast.append(ctx)

    def exitReadStat(self, ctx:GenshinLangParser.ReadStatContext):
        self.ast.append(ctx)
        variableName = ctx.IDENTIFIER().getText()
        newVar = input("Proszę wprowadź wczytywaną wartość: ")
        variables[variableName] = Value("", newVar)
