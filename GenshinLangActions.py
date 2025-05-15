import sys

from LLVMGenerator import LLVMGenerator

from generated.GenshinLangParser import GenshinLangParser
from generated.GenshinLangListener import GenshinLangListener

class GenshinASTBuilder(GenshinLangListener):
    def __init__(self):
        self.generator = LLVMGenerator()
        self.inside_stat = []
        self.ast = []
        self.inside_variable_assign = False
        self.inside_function = []

    def exitVariable(self, ctx:GenshinLangParser.VariableContext):
        if not (self.inside_stat):
            self.ast.append(ctx)

    def enterVariableAssign(self, ctx):
        if not (self.inside_stat):
            self.inside_variable_assign = True

    def exitVariableAssign(self, ctx:GenshinLangParser.VariableAssignContext):
        if not (self.inside_stat):
            self.ast.append(ctx)
            self.inside_variable_assign = False

    def exitElemToAssign(self, ctx:GenshinLangParser.ElemToAssignContext):
        if not (self.inside_stat) and not (self.inside_variable_assign):
            self.ast.append(ctx)
        
    # def exitExpression(self, ctx:GenshinLangParser.ExpressionContext):
    #     if not (self.inside_stat):
    #         self.ast.append(ctx)

    # def exitTerm(self, ctx:GenshinLangParser.TermContext):
    #     if not (self.inside_stat):
    #         self.ast.append(ctx)

    # def exitFactor(self, ctx:GenshinLangParser.FactorContext):
    #     if not (self.inside_stat):
    #         self.ast.append(ctx)

    def exitPrintStat(self, ctx:GenshinLangParser.PrintStatContext):
        if not (self.inside_stat):
            self.ast.append(ctx)

    def exitShortExpression(self, ctx: GenshinLangParser.ShortExpressionContext):
        if not (self.inside_stat):
            self.ast.append(ctx)

    def exitReadStat(self, ctx:GenshinLangParser.ReadStatContext):
        if not (self.inside_stat):
            self.ast.append(ctx)

    def enterIfStat(self, ctx: GenshinLangParser.IfStatContext):
        if not (self.inside_stat):
            self.ast.append(ctx)
        self.inside_stat.append(True)
        
    def exitIfStat(self, ctx: GenshinLangParser.IfStatContext):
        self.inside_stat.pop()

    def enterWhileStat(self, ctx: GenshinLangParser.WhileStatContext):
        self.ast.append(ctx)
        self.inside_stat.append(True)

    def exitWhileStat(self, ctx: GenshinLangParser.WhileStatContext):
        self.inside_stat.pop()

    def enterForStat(self, ctx: GenshinLangParser.ForStatContext):
        self.ast.append(ctx)
        self.inside_stat.append(True)

    def exitForStat(self, ctx: GenshinLangParser.ForStatContext):
        self.inside_stat.pop()

    def enterFunctionDeclaration(self, ctx: GenshinLangParser.FunctionDeclarationContext):
        self.ast.append(ctx)
        self.inside_stat.append(True)

    def exitFunctionDeclaration(self, ctx: GenshinLangParser.FunctionDeclarationContext):
        self.inside_stat.pop()

    def enterFunctionCall(self, ctx: GenshinLangParser.FunctionCallContext):
        if not (self.inside_stat)  and not (self.inside_variable_assign):
            self.ast.append(ctx)
    
