import sys
import re
from llvmlite import ir, binding

from .LLVMConfig import LLVMConfigMixin
from .LLVMIO import LLVMIOMixin
from .LLVMVariableHandler import LLVMVariablesMixin
from .LLVMExpression import LLVMExpressionMixin
from .LLVMStatements import LLVMStatementMixin
from .LLVMBoolExpr import LLVMBoolExprMixin
from .LLVMUtils import LLVMUtilsMixin

from generated.GenshinLangParser import GenshinLangParser

class LLVMBase(LLVMConfigMixin, LLVMIOMixin, LLVMVariablesMixin,
               LLVMExpressionMixin, LLVMStatementMixin,
               LLVMBoolExprMixin, LLVMUtilsMixin):
    
    def __init__(self):
        self.binding = binding
        self.binding.initialize()
        self.binding.initialize_native_target()
        self.binding.initialize_native_asmprinter()
        self._config_llvm()
        self._create_execution_engine()
        self._declare_print_function()
        self._declare_scanf_function()
        self.scopeStack = [{}]
        self.global_scope = {}
        self.function = None
        self.inside_function = False
        self.has_returned = None
        self.is_assigning = False
        self.functionScope = [set()]


    def generate(self, ast):
        self._generate_from_ast(ast)
        self.builder.ret(ir.Constant(ir.IntType(32), 0))
        try:
            parsed_module = binding.parse_assembly(str(self.module))
            parsed_module.verify()
        except RuntimeError as e:
            error_text = str(e)
            problematic_vars = re.findall(r'%\w+', error_text)
            if problematic_vars:
                print("Wykryto zmienne, które mogą być nieprzypisane:")
                for var in set(problematic_vars):
                    print(f"  - {var[1:]}")

            sys.exit(1)
        return str(self.module)
        

    def _generate_from_ast(self, ast):
        for node in ast:
            if isinstance(node, GenshinLangParser.VariableContext):
                var_name = node.IDENTIFIER().getText()
                if node.GLOBAL():
                    if var_name in self.global_scope:
                        print(f'Zmienna {var_name} istnieje już w zakresie globalnym!')
                        sys.exit(1)
                    else:
                        self.generate_global_variable_declaration(var_name, node.TYPE().getText())
                        continue
                elif var_name in self.scopeStack[-1]:
                    print(f'Zmienna {var_name} istnieje już w zakresie!')
                    sys.exit(1)
                self.generate_variable_declaration(var_name, node.TYPE().getText())

            if isinstance(node, GenshinLangParser.VariableAssignContext):
                var_name = node.IDENTIFIER().getText()

                if node.TYPE(): 
                    if node.GLOBAL():
                        if var_name not in self.global_scope:
                            self.generate_global_variable_declaration(var_name, node.TYPE().getText())
                        else:
                            print(f"Redeklaracja globalnej zmiennej '{var_name}'!")
                            sys.exit(1)
                    elif var_name not in self.scopeStack[-1]:
                        self.generate_variable_declaration(var_name, node.TYPE().getText())
                    else:
                        print(f"Redeklaracja zmiennej '{var_name}'!")
                        sys.exit(1)
                self.generate_variable_assignment(var_name, node.elemToAssign())

            elif isinstance(node, GenshinLangParser.PrintStatContext):
                self.generate_print_statement(node)

            elif isinstance(node, GenshinLangParser.ExpressionContext):
                self.generate_expression(node)
            
            elif isinstance(node, GenshinLangParser.ShortExpressionContext):
                self.generate_short_expression(node)

            elif isinstance(node, GenshinLangParser.ReadStatContext):
                self.read(node)
            
            elif isinstance(node, GenshinLangParser.IfStatContext):
                self.generate_if_statement(node)

            elif isinstance(node, GenshinLangParser.ForStatContext):
                self.generate_for_statement(node)

            elif isinstance(node, GenshinLangParser.WhileStatContext):
                self.generate_while_statement(node)
            
            elif isinstance(node, GenshinLangParser.FunctionDeclarationContext):
                self.generate_functionDeclaration(node)
                 
            elif isinstance(node, GenshinLangParser.FunctionCallContext):
                if not self.is_assigning:
                    self.generate_functionCall(node)

            elif isinstance(node, GenshinLangParser.ReturnStatementContext):
                if not(self.inside_function):
                    print("return może występować tylko w zasięgu funkcji!")
                    sys.exit(-1)
                self.generate_returnStatement(node)
                break
            