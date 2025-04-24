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
                if text in self.variables:
                    val = self.builder.load(self.variables[text])
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

        if variable not in self.variables:
            self.generate_variable_declaration(variable, 'double')

        var_ptr = self.variables[variable]

        fmt_global = self.module.globals.get("fmt_double")
        format_ptr = self.builder.gep(fmt_global, [ir.Constant(ir.IntType(32), 0), ir.Constant(ir.IntType(32), 0)])

        self.builder.call(self.scanf, [format_ptr, var_ptr])
        self._print_empty_line()

    def generate_if_statement(self, ctx: GenshinLangParser.InstructionContext):
        cond_val = self.generate_expression(ctx.ifStatement().condition().expression())
        zero = ir.Constant(cond_val.type, 0)
        if isinstance(cond_val.type, ir.IntType):
            cmp = self.builder.icmp_signed("!=", cond_val, zero, name="ifcond")
        else:
            cmp = self.builder.fcmp_ordered("!=", cond_val, zero, name="ifcond")

        then_bb = self.function.append_basic_block("then")
        cont_bb = self.function.append_basic_block("ifcont")

        self.builder.cbranch(cmp, then_bb, cont_bb)
        self.builder.position_at_start(then_bb)

        for inst in ctx.ifStatement().instruction():
            self.visitInstruction(inst)

        self.builder.branch(cont_bb)
        self.builder.position_at_start(cont_bb)
