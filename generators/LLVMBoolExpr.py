import sys
from llvmlite import ir
from generated.GenshinLangParser import GenshinLangParser

class LLVMBoolExprMixin:
    def _bool_expr_evaluator(self, ctx: GenshinLangParser.BoolExprContext):
        is_negated = ctx.NEG() is not None

        if ctx.COMPARSION():
            left = self.generate_expression(ctx.getChild(0))
            right = self.generate_expression(ctx.getChild(2))
            op = ctx.COMPARSION().getText()

            left, right = self._check_type_compability(left, right)

            if isinstance(left.type, ir.IntType):
                cmp_result = self._int_comparison(op, left, right)
            else:
                cmp_result = self._float_comparison(op, left, right)

            return self.builder.not_(cmp_result) if is_negated else cmp_result

        elif ctx.IDENTIFIER():
            var_name = ctx.IDENTIFIER().getText()
            if var_name in self.scopeStack[-1]:
                val = self.builder.load(self.scopeStack[-1][var_name])
                result = self.builder.icmp_unsigned("!=", val, ir.Constant(val.type, 0))
                return self.builder.not_(result) if is_negated else result
            else:
                print(f"Zmienna '{var_name}' użyta przed zadeklarowaniem!")
                sys.exit(1)

        elif ctx.BOOLEAN():
            bool_val = ctx.BOOLEAN().getText() == "true"
            result = ir.Constant(ir.IntType(1), int(not bool_val) if is_negated else int(bool_val))
            return result
        
        elif ctx.boolExpr():
            value = self._bool_expr_evaluator(ctx.boolExpr()[-1]) == "i1 1"
            result = ir.Constant(ir.IntType(1), int(not value) if is_negated else int(value))
            return result

        print("Nieobsłużony przypadek boolExpr!")
        sys.exit(1)

    def _resolve_bool_operand(self, node):
        if hasattr(node, 'BOOLEAN') and node.BOOLEAN():
            return ir.Constant(ir.IntType(1), int(node.BOOLEAN().getText() == "true"))
        elif hasattr(node, 'expression'):
            return self.generate_expression(node.expression())
        else:
            return self.generate_expression(node)

    def _int_comparison(self, op, left, right):
        if op == "==":
            return self.builder.icmp_signed("==", left, right)
        elif op == "!=":
            return self.builder.icmp_signed("!=", left, right)
        elif op == "<":
            return self.builder.icmp_signed("<", left, right)
        elif op == "<=":
            return self.builder.icmp_signed("<=", left, right)
        elif op == ">":
            return self.builder.icmp_signed(">", left, right)
        elif op == ">=":
            return self.builder.icmp_signed(">=", left, right)

    def _float_comparison(self, op, left, right):
        if op == "==":
            return self.builder.fcmp_ordered("==", left, right)
        elif op == "!=":
            return self.builder.fcmp_ordered("!=", left, right)
        elif op == "<":
            return self.builder.fcmp_ordered("<", left, right)
        elif op == "<=":
            return self.builder.fcmp_ordered("<=", left, right)
        elif op == ">":
            return self.builder.fcmp_ordered(">", left, right)
        elif op == ">=":
            return self.builder.fcmp_ordered(">=", left, right)
