import sys
import re
from llvmlite import ir
from generated.GenshinLangParser import GenshinLangParser

class LLVMStatementMixin:
    def generate_print_statement(self, print_stat_ctx: GenshinLangParser.PrintStatContext):
        for child in print_stat_ctx.printElement():
            text = child.getText()

            if child.STRING():
                val = self._keep_string_in_memory(text.strip('"'))
                fmt_global = self.module.globals.get("fmt_str")
                format_ptr = self.builder.gep(fmt_global, [ir.Constant(ir.IntType(32), 0), ir.Constant(ir.IntType(32), 0)])
                self.builder.call(self.printf, [format_ptr, val])

            elif child.IDENTIFIER():
                if text in self.scopeStack[-1]:
                    val = self.builder.load(self.scopeStack[-1][text])
                    fmt_global = self.module.globals.get("fmt_double")
                    if isinstance(val.type, ir.IntType):
                        fmt_global = self.module.globals.get("fmt_int")
                    elif isinstance(val.type, ir.FloatType):
                        val = self._convert_float_to_double(val)
                    format_ptr = self.builder.gep(fmt_global, [ir.Constant(ir.IntType(32), 0), ir.Constant(ir.IntType(32), 0)])
                    self.builder.call(self.printf, [format_ptr, val])

            elif child.expression():
                result = self.generate_expression(child.expression())
                if result is None:
                    print("Ewaluacja ekspresji zwróciła None!")
                    sys.exit(1)
                fmt_global = self.module.globals.get("fmt_double")
                if isinstance(result.type, ir.IntType):
                    fmt_global = self.module.globals.get("fmt_int")
                elif isinstance(result.type, ir.FloatType):
                    result = self._convert_float_to_double(result)
                format_ptr = self.builder.gep(fmt_global, [ir.Constant(ir.IntType(32), 0), ir.Constant(ir.IntType(32), 0)])
                self.builder.call(self.printf, [format_ptr, result])


            else:
                if re.match(r'^-?\d+\.\d+$', text):
                    value = ir.Constant(ir.FloatType, text)
                    fmt_global = self.module.globals.get("fmt_float")
                    format_ptr = self.builder.gep(fmt_global, [ir.Constant(ir.IntType(32), 0), ir.Constant(ir.IntType(32), 0)])
                    self.builder.call(self.printf, [format_ptr, value])

                if re.match(r'^-?\d+$', text):
                    value = ir.Constant(ir.IntType(32), text)
                    fmt_global = self.module.globals.get("fmt_int")
                    format_ptr = self.builder.gep(fmt_global, [ir.Constant(ir.IntType(32), 0), ir.Constant(ir.IntType(32), 0)])
                    self.builder.call(self.printf, [format_ptr, value])

        self._print_empty_line()

    def read(self, node):
        variable = node.IDENTIFIER().getText()

        if variable not in self.scopeStack[-1]:
            self.generate_variable_declaration(variable, 'double')

        var_ptr = self.scopeStack[-1][variable]

        fmt_global = self.module.globals.get("fmt_double")
        format_ptr = self.builder.gep(fmt_global, [ir.Constant(ir.IntType(32), 0), ir.Constant(ir.IntType(32), 0)])

        self.builder.call(self.scanf, [format_ptr, var_ptr])
        self._print_empty_line()

    def generate_if_statement(self, ctx: GenshinLangParser.IfStatContext):
        cond = self._bool_expr_evaluator(ctx.boolExpr())
        if cond is None:
            print("Ewaluacja warunku zwróciła None!")
            sys.exit(1)

        then_block = self.builder.append_basic_block('if_then')
        else_block = self.builder.append_basic_block('if_else') if ctx.block(1) else None
        merge_block = self.builder.append_basic_block('if_end')

        if else_block:
            self.builder.cbranch(cond, then_block, else_block)
        else:
            self.builder.cbranch(cond, then_block, merge_block)

        self.builder.position_at_end(then_block)
        statements = [i.getChild(0) for i in list(ctx.block(0).getChildren())]
        self._generate_from_ast(statements)
        self.builder.branch(merge_block)

        if else_block:
            self.builder.position_at_end(else_block)
            statements = [i.getChild(0) for i in list(ctx.block(1).getChildren())]
            self._generate_from_ast(statements)
            self.builder.branch(merge_block)

        self.builder.position_at_end(merge_block)

    def generate_while_statement(self, ctx: GenshinLangParser.WhileStatContext):
        cond_block = self.builder.append_basic_block('while_cond')
        body_block = self.builder.append_basic_block('while_body')
        end_block = self.builder.append_basic_block('while_end')

        self.builder.branch(cond_block)

        self.builder.position_at_end(cond_block)
        
        cond = self._bool_expr_evaluator(ctx.boolExpr())
        if cond is None:
            print("Ewaluacja warunku zwróciła None!")
            sys.exit(1)

        self.builder.cbranch(cond, body_block, end_block)

        self.builder.position_at_end(body_block)
        
        statements = [i.getChild(0) for i in list(ctx.block().getChildren())]
        self._generate_from_ast(statements)

        self.builder.branch(cond_block)
        self.builder.position_at_end(end_block)

    def generate_for_statement(self, ctx: GenshinLangParser.ForStatContext):
        cond_block = self.builder.append_basic_block('for_cond')
        body_block = self.builder.append_basic_block('for_body')
        end_block = self.builder.append_basic_block('for_end')
        
        if ctx.variableAssign():
            if ctx.variableAssign()[0].TYPE():
                self.generate_variable_declaration(ctx.variableAssign(0).IDENTIFIER().getText(), ctx.variableAssign()[0].TYPE().getText())

            self.generate_variable_assignment(ctx.variableAssign(0).IDENTIFIER().getText(), ctx.variableAssign()[0].elemToAssign())

        self.builder.branch(cond_block)
        self.builder.position_at_end(cond_block)

        cond = self._bool_expr_evaluator(ctx.boolExpr())
        if cond is None:
            print("Ewaluacja warunku zwróciła None!")
            sys.exit(1)


        self.builder.cbranch(cond, body_block, end_block)

        self.builder.position_at_end(body_block)
        
        statements = [i.getChild(0) for i in list(ctx.block().getChildren())]
        self._generate_from_ast(statements)
        if ctx.variableAssign(1):
            if ctx.variableAssign(1).TYPE():
                print(f"W tym miejscu nie można zadeklarować zmiennej!")
                sys.exit(1)

            self.generate_variable_assignment(ctx.variableAssign(1).IDENTIFIER().getText(), ctx.variableAssign(1).elemToAssign())
        elif ctx.shortExpression():
            self.generate_short_expression(ctx.shortExpression())

        self.builder.branch(cond_block)
        self.builder.position_at_end(end_block)

                

