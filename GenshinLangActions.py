import sys

from LLVMGenerator import LLVMGenerator

from generated.GenshinLangParser import GenshinLangParser
from generated.GenshinLangListener import GenshinLangListener

class GenshinASTBuilder(GenshinLangListener):
    def __init__(self):
        self.generator = LLVMGenerator()
        self.ast = []

    def exitVariable(self, ctx:GenshinLangParser.VariableContext):
        self.ast.append(ctx)

    def exitVariableAssign(self, ctx:GenshinLangParser.VariableAssignContext):
        self.ast.append(ctx)

    def exitElemToAssign(self, ctx:GenshinLangParser.ElemToAssignContext):
        self.ast.append(ctx)
        
    def exitExpression(self, ctx:GenshinLangParser.ExpressionContext):
        self.ast.append(ctx)

    def exitTerm(self, ctx:GenshinLangParser.TermContext):
        self.ast.append(ctx)

    def exitFactor(self, ctx:GenshinLangParser.FactorContext):
        self.ast.append(ctx)

    def exitPrintStat(self, ctx:GenshinLangParser.PrintStatContext):
        self.ast.append(ctx)

    def exitReadStat(self, ctx:GenshinLangParser.ReadStatContext):
        self.ast.append(ctx)
