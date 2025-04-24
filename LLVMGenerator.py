import sys
import re
from llvmlite import ir, binding

from generated.GenshinLangParser import GenshinLangParser
from generated.GenshinLangListener import GenshinLangListener

class LLVMGenerator():
    # def __init__(self):
    #     self.binding = binding
    #     self.binding.initialize()
    #     self.binding.initialize_native_target()
    #     self.binding.initialize_native_asmprinter()
    #     self._config_llvm()
    #     self._create_execution_engine()
    #     self._declare_print_function()
    #     self._declare_scanf_function()
    #     self.variables = {}

    # def _config_llvm(self):
    #     self.module = ir.Module(name=__file__)
    #     self.module.triple = self.binding.get_default_triple()
    #     func_type = ir.FunctionType(ir.IntType(32), [], False)
    #     main_func = ir.Function(self.module, func_type, name="main")
    #     block = main_func.append_basic_block(name="entry")
    #     self.builder = ir.IRBuilder(block)
    #     self.voidptr_ty = ir.IntType(8).as_pointer()

        # fmt_str = ir.GlobalVariable(self.module, ir.ArrayType(ir.IntType(8), 4), name="fmt_str")
        # fmt_str.initializer = ir.Constant(ir.ArrayType(ir.IntType(8), 4), bytearray(b"%s\x20\0"))

        # fmt_int_global = ir.GlobalVariable(self.module, ir.ArrayType(ir.IntType(8), 4), name="fmt_int")
        # fmt_int_global.initializer = ir.Constant(ir.ArrayType(ir.IntType(8), 4), bytearray(b"%d\x20\0"))

        # fmt_float_global = ir.GlobalVariable(self.module, ir.ArrayType(ir.IntType(8), 4), name="fmt_float")
        # fmt_float_global.initializer = ir.Constant(ir.ArrayType(ir.IntType(8), 4), bytearray(b"%f\x20\0"))

        # fmt_double_global = ir.GlobalVariable(self.module, ir.ArrayType(ir.IntType(8), 5), name="fmt_double")
        # fmt_double_global.initializer = ir.Constant(ir.ArrayType(ir.IntType(8), 5), bytearray(b"%lf\x20\0"))

        # fmt_newline_global = ir.GlobalVariable(self.module, ir.ArrayType(ir.IntType(8), 2), name="fmt_newline")
        # fmt_newline_global.initializer = ir.Constant(ir.ArrayType(ir.IntType(8), 2), bytearray(b"\n\0"))

    # def _create_execution_engine(self):
    #     target = self.binding.Target.from_default_triple()
    #     target_machine = target.create_target_machine()
    #     backing_mod = binding.parse_assembly("")
    #     engine = binding.create_mcjit_compiler(backing_mod, target_machine)
    #     self.engine = engine

    # def _declare_print_function(self):
    #     voidptr_ty = ir.IntType(8).as_pointer()
    #     printf_ty = ir.FunctionType(ir.IntType(32), [voidptr_ty], var_arg=True)
    #     self.printf = ir.Function(self.module, printf_ty, name="printf")

    #     fflush_ty = ir.FunctionType(ir.IntType(32), [self.voidptr_ty])
    #     self.fflush = ir.Function(self.module, fflush_ty, name="fflush")

    # def _declare_scanf_function(self):
    #     scanf_ty = ir.FunctionType(ir.IntType(32), [self.voidptr_ty], var_arg=True)
    #     self.scanf = ir.Function(self.module, scanf_ty, name="scanf")

    # def generate(self, ast):
    #     self._generate_from_ast(ast)
    #     self.builder.ret(ir.Constant(ir.IntType(32), 0))
    #     return str(self.module)

    # def _generate_from_ast(self, ast):
    #     for node in ast:
    #         if isinstance(node, GenshinLangParser.VariableContext):
    #             var_name = node.IDENTIFIER().getText()
    #             if var_name in self.variables:
    #                 print(f'Zmienna {var_name} istnieje już w zakresie!')
    #                 sys.exit(1)
    #             self.generate_variable_declaration(var_name, node.TYPE().getText())

    #         if isinstance(node, GenshinLangParser.VariableAssignContext):
    #             var_name = node.IDENTIFIER().getText()
    #             if node.TYPE(): 
    #                 if var_name not in self.variables:
    #                     self.generate_variable_declaration(var_name, node.TYPE().getText())
    #                 else:
    #                     print(f"Redeklaracja zmiennej '{var_name}'!")
    #                     sys.exit(1)
    #             if var_name in self.variables:
    #                 self.generate_variable_assignment(var_name, node.elemToAssign())
    #             else:
    #                 print(f"Przypisanie do niezadeklarowanej zmiennej '{var_name}'!")
    #                 sys.exit(1)

    #         elif isinstance(node, GenshinLangParser.PrintStatContext):
    #             self.generate_print_statement(node)

    #         elif isinstance(node, GenshinLangParser.ExpressionContext):
    #             self.generate_expression(node)

    #         elif isinstance(node, GenshinLangParser.ReadStatContext):
    #             self.read(node)
            
    #         elif isinstance(node, GenshinLangParser.IfStatContext):
    #             self.generate_if_statement(node)

    # def generate_variable_declaration(self, ident, type):
    #     if type == 'int':
    #         ptr = self.builder.alloca(ir.IntType(32), name=ident)
    #     elif type == 'float':
    #         ptr = self.builder.alloca(ir.FloatType(), name=ident)
    #     elif type == 'double':
    #         ptr = self.builder.alloca(ir.DoubleType(), name=ident)
    #     self.variables[ident] = ptr

    # def generate_variable_assignment(self, ident, value: GenshinLangParser.ElemToAssignContext):
    #     ptr = self.variables.get(ident)
    #     if ptr is None:
    #         print(f"Zmienna '{ident}' jest niezadeklarowana!")
    #         sys.exit(1)

    #     expression_value = self.generate_expression(value.expression())

    #     if isinstance(self.variables[ident].type.pointee, ir.FloatType):
    #         expression_value = self._convert_double_to_float(expression_value)
    #     elif isinstance(self.variables[ident].type.pointee, ir.IntType):
    #         expression_value = self._convert_double_to_int(expression_value)

    #     if expression_value is None:
    #         print(f"Błąd ewaluacji eksprecji '{value}'!")
    #         sys.exit(1)
        
    #     self.builder.store(expression_value, ptr)

    # def read(self, node):
    #     variable = node.IDENTIFIER().getText()

    #     if variable not in self.variables:
    #         self.generate_variable_declaration(variable, 'double')

    #     var_ptr = self.variables[variable]

    #     fmt_global = self.module.globals.get("fmt_double")
    #     format_ptr = self.builder.gep(fmt_global, [ir.Constant(ir.IntType(32), 0), ir.Constant(ir.IntType(32), 0)])

    #     self.builder.call(self.scanf, [format_ptr, var_ptr])
    #     self._print_empty_line()

       

    # def generate_print_statement(self, print_stat_ctx: GenshinLangParser.PrintStatContext):
    #     for child in print_stat_ctx.printElement():
    #         text = child.getText()

    #         if child.STRING():
    #             val = self._keep_string_in_memory(text.strip('"'))
    #             fmt_global = self.module.globals.get("fmt_str")
    #             format_ptr = self.builder.gep(fmt_global, [ir.Constant(ir.IntType(32), 0), ir.Constant(ir.IntType(32), 0)])
    #             self.builder.call(self.printf, [format_ptr, val])

    #         elif child.IDENTIFIER():
    #             if text in self.variables:
    #                 val = self.builder.load(self.variables[text])
    #                 fmt_global = self.module.globals.get("fmt_double")
    #                 if isinstance(val.type, ir.IntType):
    #                     fmt_global = self.module.globals.get("fmt_int")
    #                 elif isinstance(val.type, ir.FloatType):
    #                     val = self._convert_float_to_double(val)
    #                 format_ptr = self.builder.gep(fmt_global, [ir.Constant(ir.IntType(32), 0), ir.Constant(ir.IntType(32), 0)])
    #                 self.builder.call(self.printf, [format_ptr, val])

    #         elif child.expression():
    #             result = self.generate_expression(child.expression())
    #             if result is None:
    #                 print("Ewaluacja ekspresji zwróciła None!")
    #                 sys.exit(1)
    #             fmt_global = self.module.globals.get("fmt_double")
    #             if isinstance(result.type, ir.IntType):
    #                 fmt_global = self.module.globals.get("fmt_int")
    #             elif isinstance(result.type, ir.FloatType):
    #                 result = self._convert_float_to_double(result)
    #             format_ptr = self.builder.gep(fmt_global, [ir.Constant(ir.IntType(32), 0), ir.Constant(ir.IntType(32), 0)])
    #             self.builder.call(self.printf, [format_ptr, result])


    #         else:
    #             if re.match(r'^-?\d+\.\d+$', text):
    #                 value = ir.Constant(ir.FloatType, text)
    #                 fmt_global = self.module.globals.get("fmt_float")
    #                 format_ptr = self.builder.gep(fmt_global, [ir.Constant(ir.IntType(32), 0), ir.Constant(ir.IntType(32), 0)])
    #                 self.builder.call(self.printf, [format_ptr, value])

    #             if re.match(r'^-?\d+$', text):
    #                 value = ir.Constant(ir.IntType(32), text)
    #                 fmt_global = self.module.globals.get("fmt_int")
    #                 format_ptr = self.builder.gep(fmt_global, [ir.Constant(ir.IntType(32), 0), ir.Constant(ir.IntType(32), 0)])
    #                 self.builder.call(self.printf, [format_ptr, value])

    #     self._print_empty_line()

    # def _keep_string_in_memory(self, value):
    #     str_len = len(value) + 1
        
    #     str_alloca = self.builder.alloca(ir.ArrayType(ir.IntType(8), str_len))

    #     for i, byte in enumerate(value.encode("utf8") + b"\0"):
    #         ptr = self.builder.gep(str_alloca, [ir.Constant(ir.IntType(32), 0), ir.Constant(ir.IntType(32), i)])
    #         self.builder.store(ir.Constant(ir.IntType(8), byte), ptr)
    #     return str_alloca
    
    # def _print_empty_line(self):
    #     fmt_newline_global = self.module.globals.get("fmt_newline")
    #     format_ptr = self.builder.gep(fmt_newline_global, [ir.Constant(ir.IntType(32), 0), ir.Constant(ir.IntType(32), 0)])
    #     self.builder.call(self.printf, [format_ptr])
    #     self.builder.call(self.fflush, [ir.Constant(ir.IntType(8).as_pointer(), None)])
    
    # def generate_expression(self, ctx: GenshinLangParser.ExpressionContext):
    #     value1 = self.generate_term(ctx.term(0))
    #     for i in range(1, len(ctx.term())):
    #         operator = list(ctx.getChildren())[2 * i - 1].getText()
    #         value2 = self.generate_term(ctx.term(i))

    #         if value2 is None:
    #             print(f"Nie udało się wygenerować drugiego operandu dla operatora '{operator}'!")
    #             sys.exit(1)

    #         value1, value2 = self._check_type_compability(value1, value2)

    #         if isinstance(value1.type, ir.IntType) and isinstance(value2.type, ir.IntType):
    #             if operator == "+":
    #                 value1 = self.builder.add(value1, value2, name="addtmp")
    #             elif operator == "-":
    #                 value1 = self.builder.sub(value1, value2, name="subtmp")
    #         else:
    #             if operator == "+":
    #                 value1 = self.builder.fadd(value1, value2, name="addtmp")
    #             elif operator == "-":
    #                 value1 = self.builder.fsub(value1, value2, name="subtmp")

    #     return value1

    # def generate_term(self, ctx: GenshinLangParser.TermContext):
    #     value1 = self.generate_factor(ctx.factor(0))
    #     for i in range(1, len(ctx.factor())):
    #         operator = list(ctx.getChildren())[2 * i - 1].getText()
    #         value2 = self.generate_factor(ctx.factor(i))
    #         value1, value2 = self._check_type_compability(value1, value2)

    #         if isinstance(value1.type, ir.IntType) and isinstance(value2.type, ir.IntType):
    #             if operator == "*":
    #                 value1 = self.builder.mul(value1, value2, name="multmp")
    #             elif operator == "/":
    #                 value1 = self.builder.sdiv(value1, value2, name="divtmp")
    #         else:
    #             if operator == "*":
    #                 value1 = self.builder.fmul(value1, value2, name="multmp")
    #             elif operator == "/":
    #                 value1 = self.builder.fdiv(value1, value2, name="divtmp")

    #     return value1


    # def generate_factor(self, ctx: GenshinLangParser.FactorContext):
    #     if ctx.MINUS():
    #         return ir.Constant(ir.DoubleType(), -1*float(ctx.NUMBER().getText()))
    #     elif ctx.NUMBER():
    #         return ir.Constant(ir.DoubleType(), float(ctx.NUMBER().getText()))
    #     elif ctx.IDENTIFIER():
    #         if ctx.IDENTIFIER().getText() in self.variables:
    #             ptr = self.variables[ctx.IDENTIFIER().getText()]
    #             return self.builder.load(ptr)
    #         else:
    #             print(f"Zmienna '{ctx.IDENTIFIER().getText()}' użyta przed zadeklarowaniem!")
    #             sys.exit(1)        
    #     else:
    #         print("Nieobsłużony typ czynnika!")
    #         sys.exit(1)

    def generate_if_statement(self, ctx: GenshinLangParser.IfStatContext):
        print(self._bool_expr_evaluator(ctx.boolExpr()))

    def _bool_expr_evaluator (self, ctx: GenshinLangParser.BoolExprContext):
        if ctx.IDENTIFIER():
            if ctx.IDENTIFIER().getText() in self.variables:
                ptr = self.variables[ctx.IDENTIFIER().getText()]
                return self.builder.load(ptr)
            else:
                print(f"Zmienna '{ctx.IDENTIFIER().getText()}' użyta przed zadeklarowaniem!")
                sys.exit(1)        
    # def _check_type_compability(self, value1, value2):
    #     type1 = value1.type
    #     type2 = value2.type

    #     if type1 == type2:
    #         return value1, value2

    #     if isinstance(type1, ir.IntType) and isinstance(type2, (ir.FloatType, ir.DoubleType)):
    #         return self._convert_int_to_float(value1, type2), value2

    #     if isinstance(type2, ir.IntType) and isinstance(type1, (ir.FloatType, ir.DoubleType)):
    #         return value1, self._convert_int_to_float(value2, type1)

    #     if isinstance(type1, ir.FloatType) and isinstance(type2, ir.DoubleType):
    #         return self._convert_float_to_double(value1), value2

    #     if isinstance(type1, ir.DoubleType) and isinstance(type2, ir.FloatType):
    #         return value1, self._convert_float_to_double(value2)

    #     if isinstance(type1, (ir.FloatType, ir.DoubleType)) and isinstance(type2, (ir.FloatType, ir.DoubleType)):
    #         if isinstance(type1, ir.FloatType):
    #             return self._convert_float_to_double(value1), value2
    #         else:
    #             return value1, self._convert_float_to_double(value2)

    #     return value1, value2

    # def _convert_int_to_float(self, value, dest_type):
    #     if isinstance(value.type, ir.IntType):
    #         if dest_type == ir.FloatType():
    #             return self.builder.sitofp(value, ir.FloatType())
    #         elif dest_type == ir.DoubleType():
    #             return self.builder.sitofp(value, ir.DoubleType())
    #     return value

    # def _convert_float_to_double(self, value):
    #     if isinstance(value.type, ir.FloatType):
    #         return self.builder.fpext(value, ir.DoubleType())
    #     return value
    
    # def _convert_double_to_float(self, value):
    #     return self.builder.fptrunc(value, ir.FloatType())
    
    # def _convert_double_to_int(self, value):
    #     return self.builder.fptosi(value, ir.IntType(32))