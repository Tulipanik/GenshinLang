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
        cond_value = self._bool_expr_evaluator(ctx.boolExpr())
        then_block = self.func.append_basic_block(name="then")
        else_block = self.func.append_basic_block(name="else") if ctx.block(1) else None
        endif_block = self.func.append_basic_block(name="endif")

        # Warunkowy skok
        if else_block:
            self.builder.cbranch(cond_value, then_block, else_block)
        else:
            self.builder.cbranch(cond_value, then_block, endif_block)

        # THEN
        self.builder.position_at_start(then_block)
        self.visit(ctx.block(0))  # odwiedzamy pierwszy blok (if)
        if not self.builder.block.is_terminated:
            self.builder.branch(endif_block)

        # ELSE (jeśli istnieje)
        if else_block:
            self.builder.position_at_start(else_block)
            self.visit(ctx.block(1))  # odwiedzamy blok else
            if not self.builder.block.is_terminated:
                self.builder.branch(endif_block)

        # ENDIF
        self.builder.position_at_start(endif_block)
