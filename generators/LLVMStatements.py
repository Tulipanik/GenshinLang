import sys
import re
import copy
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

        self.scopeStack.append({})

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

        self.scopeStack.pop()
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

        self.scopeStack.append({})
        
        statements = [i.getChild(0) for i in list(ctx.block().getChildren())]
        self._generate_from_ast(statements)

        self.scopeStack.pop()

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

        self.scopeStack.append({})
        
        statements = [i.getChild(0) for i in list(ctx.block().getChildren())]
        self._generate_from_ast(statements)

        self.scopeStack.pop()

        if ctx.variableAssign(1):
            if ctx.variableAssign(1).TYPE():
                print(f"W tym miejscu nie można zadeklarować zmiennej!")
                sys.exit(1)

            self.generate_variable_assignment(ctx.variableAssign(1).IDENTIFIER().getText(), ctx.variableAssign(1).elemToAssign())
        elif ctx.shortExpression():
            self.generate_short_expression(ctx.shortExpression())

        self.builder.branch(cond_block)
        self.builder.position_at_end(end_block)

    def generate_functionDeclaration(self, ctx: GenshinLangParser.FunctionDeclarationContext):
        self.inside_function = True
        original_name = ctx.IDENTIFIER().getText()

        self.functionScope[-1].add(original_name)
        self.functionScope.append(set(self.functionScope[-1]))
        
        if self.function:
            func_name = f"{self.function.name}_{original_name}"
        else:
            func_name = original_name

        suffix = 0
        base_name = func_name
        while func_name in self.module.globals:
            suffix += 1
            func_name = f"{base_name}_{suffix}"

        params = []
        param_types = []

        if ctx.paramList():
            param_list = list(ctx.paramList().getChildren())
            for i in range(0, len(param_list), 3): 
                if i + 1 < len(param_list):
                    type_str = param_list[i].getText()
                    param_name = param_list[i + 1].getText()
                    params.append(param_name)
                    if type_str == 'int':
                        param_types.append(ir.IntType(32))
                    elif type_str == 'float':
                        param_types.append(ir.FloatType())
                    elif type_str == 'double':
                        param_types.append(ir.DoubleType())
                    elif type_str == 'boolean':
                        param_types.append(ir.IntType(1))
                    elif type_str == 'var':
                        param_types.append(ir.DoubleType())
                    else:
                        print(f"Unknown type: {type_str}")
                        sys.exit(1)

        if self.function_contains_return(ctx.block()):
            return_type = ir.DoubleType()
        else:
            return_type = ir.VoidType()

        func_type = ir.FunctionType(return_type, param_types)
        func = ir.Function(self.module, func_type, name=func_name)
        self.scopeStack[-1][original_name] = func

        entry_block = func.append_basic_block('entry')

        old_builder = self.builder
        old_function = self.function

        self.builder = ir.IRBuilder(entry_block)
        self.function = func
        self.return_type = return_type

        self.scopeStack.append({})

        for i, param_name in enumerate(params):
            param_ptr = self.builder.alloca(param_types[i], name=param_name)
            self.builder.store(func.args[i], param_ptr)
            self.scopeStack[-1][param_name] = param_ptr
        statements = [i.getChild(0) for i in list(ctx.block().getChildren())]
        self._generate_from_ast(statements)
        


        if not self.builder.block.is_terminated:
            if isinstance(return_type, ir.VoidType):
                self.builder.ret_void()
            else:
                self.builder.ret(ir.Constant(ir.DoubleType(), 0.0))  

        self.return_type = None
        self.builder = old_builder
        self.function = old_function
        self.has_returned = None
        self.inside_function = True
        self.scopeStack.pop()
        self.functionScope.pop()

    def function_contains_return(self, block_ctx):
        for child in block_ctx.getChildren():
            if child.getText() == 'return':
                return True
            if hasattr(child, 'getChildren'):
                if self.function_contains_return(child):
                    return True
        return False


    def generate_returnStatement(self, ctx: GenshinLangParser.ReturnStatementContext):
        if ctx.expression():
            value = self.generate_expression(ctx.expression())
            self.builder.ret(value)
        else:
            self.builder.ret_void()
        self.has_returned = True

    
    def generate_functionCall(self, ctx: GenshinLangParser.FunctionCallContext):
        func_name = ctx.IDENTIFIER().getText()

        if not(func_name in self.functionScope[-1]):
            print("Funkcja nie istnieje w podanym zasięgu!")
            sys.exit(-1)

        func = None
        for scope in reversed(self.scopeStack):
            if func_name in scope:
                func = scope[func_name]
                break

        if not func:
            func = self.module.globals.get(func_name)

        if not func or not isinstance(func, ir.Function):
            print(f"Funkcja '{func_name}' nie została zadeklarowana!")
            sys.exit(1)

        args = []
        if ctx.argumentList():
            expected_types = [arg.type for arg in func.args]
            arg_nodes = [child for child in ctx.argumentList().getChildren() if child.getText() != ',']

            if len(arg_nodes) != len(expected_types):
                print(f"Funkcja '{func_name}' oczekuje {len(expected_types)} argumentów, otrzymano {len(arg_nodes)}")
                sys.exit(1)

            for arg_node, expected_type in zip(arg_nodes, expected_types):
                arg_value = self.generate_expression(arg_node)

                if arg_value.type != expected_type:
                    if isinstance(expected_type, ir.IntType) and isinstance(arg_value.type, ir.DoubleType):
                        arg_value = self.builder.fptosi(arg_value, expected_type)
                    elif isinstance(expected_type, ir.DoubleType) and isinstance(arg_value.type, ir.IntType):
                        arg_value = self.builder.sitofp(arg_value, expected_type)
                    else:
                        print(f"Nie można przekonwertować typu argumentu {arg_value.type} na {expected_type}")
                        sys.exit(1)

                args.append(arg_value)

        return self.builder.call(func, args, name=f"{func_name}_call")

                

