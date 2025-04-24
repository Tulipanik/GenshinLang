import sys
from llvmlite import ir
from generated.GenshinLangParser import GenshinLangParser

class LLVMBoolExprMixin:
    def _bool_expr_evaluator(self, ctx: GenshinLangParser.BoolExprContext):
        # NOT operator
        is_negated = ctx.NEG() is not None

        # Case 1: BOOLEAN | expression COMPARSION BOOLEAN | expression
        if ctx.COMPARSION():
            left = self._resolve_bool_operand(ctx.getChild(0))
            right = self._resolve_bool_operand(ctx.getChild(2))
            op = ctx.COMPARSION().getText()

            left, right = self._check_type_compability(left, right)

            if isinstance(left.type, ir.IntType):
                cmp_result = self._int_comparison(op, left, right)
            else:
                cmp_result = self._float_comparison(op, left, right)

            return self.builder.not_(cmp_result) if is_negated else cmp_result

        # Case 2: IDENTIFIER or NEG IDENTIFIER
        elif ctx.IDENTIFIER():
            var_name = ctx.IDENTIFIER().getText()
            if var_name in self.variables:
                val = self.builder.load(self.variables[var_name])
                result = self.builder.icmp_unsigned("!=", val, ir.Constant(val.type, 0))
                return self.builder.not_(result) if is_negated else result
            else:
                print(f"Zmienna '{var_name}' użyta przed zadeklarowaniem!")
                sys.exit(1)

        # Case 3: BOOLEAN or NEG BOOLEAN
        elif ctx.BOOLEAN():
            bool_val = ctx.BOOLEAN().getText() == "true"
            result = ir.Constant(ir.IntType(1), int(not bool_val) if is_negated else int(bool_val))
            return result

        print("Nieobsłużony przypadek boolExpr!")
        sys.exit(1)

    def _resolve_bool_operand(self, node):
        # Check if it's BOOLEAN or expression
        if hasattr(node, 'BOOLEAN') and node.BOOLEAN():
            return ir.Constant(ir.IntType(1), int(node.BOOLEAN().getText() == "true"))
        elif hasattr(node, 'expression'):
            return self.generate_expression(node.expression())
        else:
            return self.generate_expression(node)  # fallback

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
