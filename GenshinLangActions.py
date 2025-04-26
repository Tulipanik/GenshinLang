import sys

from LLVMGenerator import LLVMGenerator

from generated.GenshinLangParser import GenshinLangParser
from generated.GenshinLangListener import GenshinLangListener

class GenshinASTBuilder(GenshinLangListener):
    def __init__(self):
        self.generator = LLVMGenerator()
        self.inside_if_stat = []
        self.ast = []

    def exitVariable(self, ctx:GenshinLangParser.VariableContext):
        if not (self.inside_if_stat):
            self.ast.append(ctx)
            print(ctx.getText())

    def exitVariableAssign(self, ctx:GenshinLangParser.VariableAssignContext):
        if not (self.inside_if_stat):
            self.ast.append(ctx)
            print(ctx.getText())

    def exitElemToAssign(self, ctx:GenshinLangParser.ElemToAssignContext):
        if not (self.inside_if_stat):
            self.ast.append(ctx)
        
    def exitExpression(self, ctx:GenshinLangParser.ExpressionContext):
        if not (self.inside_if_stat):
            self.ast.append(ctx)

    def exitTerm(self, ctx:GenshinLangParser.TermContext):
        if not (self.inside_if_stat):
            self.ast.append(ctx)

    def exitFactor(self, ctx:GenshinLangParser.FactorContext):
        if not (self.inside_if_stat):
            self.ast.append(ctx)

    def exitPrintStat(self, ctx:GenshinLangParser.PrintStatContext):
        if not (self.inside_if_stat):
            self.ast.append(ctx)

    def exitReadStat(self, ctx:GenshinLangParser.ReadStatContext):
        if not (self.inside_if_stat):
            self.ast.append(ctx)

    def enterIfStat(self, ctx: GenshinLangParser.IfStatContext):
        self.ast.append(ctx)
        self.inside_if_stat.append(True)
        
    def exitIfStat(self, ctx: GenshinLangParser.IfStatContext):
        self.inside_if_stat.pop()

    def enterWhileStat(self, ctx: GenshinLangParser.WhileStatContext):
        self.ast.append(ctx)
        self.inside_if_stat.append(True)

    def exitWhileStat(self, ctx: GenshinLangParser.WhileStatContext):
        self.inside_if_stat.pop()
    
