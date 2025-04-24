import sys
from llvmlite import ir
from generated.GenshinLangParser import GenshinLangParser

class LLVMExpressionMixin:
    def generate_expression(self, ctx: GenshinLangParser.ExpressionContext):
        value1 = self.generate_term(ctx.term(0))
        for i in range(1, len(ctx.term())):
            operator = list(ctx.getChildren())[2 * i - 1].getText()
            value2 = self.generate_term(ctx.term(i))

            if value2 is None:
                print(f"Nie udało się wygenerować drugiego operandu dla operatora '{operator}'!")
                sys.exit(1)

            value1, value2 = self._check_type_compability(value1, value2)

            if isinstance(value1.type, ir.IntType) and isinstance(value2.type, ir.IntType):
                if operator == "+":
                    value1 = self.builder.add(value1, value2, name="addtmp")
                elif operator == "-":
                    value1 = self.builder.sub(value1, value2, name="subtmp")
            else:
                if operator == "+":
                    value1 = self.builder.fadd(value1, value2, name="addtmp")
                elif operator == "-":
                    value1 = self.builder.fsub(value1, value2, name="subtmp")

        return value1

    def generate_term(self, ctx: GenshinLangParser.TermContext):
        value1 = self.generate_factor(ctx.factor(0))
        for i in range(1, len(ctx.factor())):
            operator = list(ctx.getChildren())[2 * i - 1].getText()
            value2 = self.generate_factor(ctx.factor(i))
            value1, value2 = self._check_type_compability(value1, value2)

            if isinstance(value1.type, ir.IntType) and isinstance(value2.type, ir.IntType):
                if operator == "*":
                    value1 = self.builder.mul(value1, value2, name="multmp")
                elif operator == "/":
                    value1 = self.builder.sdiv(value1, value2, name="divtmp")
            else:
                if operator == "*":
                    value1 = self.builder.fmul(value1, value2, name="multmp")
                elif operator == "/":
                    value1 = self.builder.fdiv(value1, value2, name="divtmp")

        return value1


    def generate_factor(self, ctx: GenshinLangParser.FactorContext):
        if ctx.MINUS():
            return ir.Constant(ir.DoubleType(), -1*float(ctx.NUMBER().getText()))
        elif ctx.NUMBER():
            return ir.Constant(ir.DoubleType(), float(ctx.NUMBER().getText()))
        elif ctx.IDENTIFIER():
            if ctx.IDENTIFIER().getText() in self.scopeStack[-1]:
                ptr = self.scopeStack[-1][ctx.IDENTIFIER().getText()]
                return self.builder.load(ptr)
            else:
                print(f"Zmienna '{ctx.IDENTIFIER().getText()}' użyta przed zadeklarowaniem!")
                sys.exit(1)        
        else:
            print("Nieobsłużony typ czynnika!")
            sys.exit(1)