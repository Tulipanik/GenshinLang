import sys
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
        self.variables = {}
        self.scopeStack = [{}]

    def generate(self, ast):
        self._generate_from_ast(ast)
        self.builder.ret(ir.Constant(ir.IntType(32), 0))
        return str(self.module)

    def _generate_from_ast(self, ast):
        # print(ast)
        for node in ast:
            # print(isinstance(node, GenshinLangParser.PrintStatContext))
            if isinstance(node, GenshinLangParser.VariableContext):
                var_name = node.IDENTIFIER().getText()
                if var_name in self.variables:
                    print(f'Zmienna {var_name} istnieje już w zakresie!')
                    sys.exit(1)
                self.generate_variable_declaration(var_name, node.TYPE().getText())

            if isinstance(node, GenshinLangParser.VariableAssignContext):
                var_name = node.IDENTIFIER().getText()
                if node.TYPE(): 
                    if var_name not in self.scopeStack[-1]:
                        self.generate_variable_declaration(var_name, node.TYPE().getText())
                    else:
                        print(f"Redeklaracja zmiennej '{var_name}'!")
                        sys.exit(1)
                if var_name in  self.scopeStack[-1]:
                    self.generate_variable_assignment(var_name, node.elemToAssign())
                else:
                    print(f"Przypisanie do niezadeklarowanej zmiennej '{var_name}'!")
                    sys.exit(1)

            elif isinstance(node, GenshinLangParser.PrintStatContext):
                print("siema")
                self.generate_print_statement(node)

            elif isinstance(node, GenshinLangParser.ExpressionContext):
                self.generate_expression(node)
            
            elif isinstance(node, GenshinLangParser.ShortExpressionContext):
                print("elo")
                self.generate_short_expression(node)

            elif isinstance(node, GenshinLangParser.ReadStatContext):
                self.read(node)
            
            elif isinstance(node, GenshinLangParser.IfStatContext):
                self.generate_if_statement(node)

            elif isinstance(node, GenshinLangParser.WhileStatContext):
                self.generate_while_statement(node)