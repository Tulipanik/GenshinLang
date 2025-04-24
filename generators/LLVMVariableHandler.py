import sys
from llvmlite import ir
from generated.GenshinLangParser import GenshinLangParser

class LLVMVariablesMixin:
    def generate_variable_declaration(self, ident, type):
        if type == 'int':
            ptr = self.builder.alloca(ir.IntType(32), name=ident)
        elif type == 'float':
            ptr = self.builder.alloca(ir.FloatType(), name=ident)
        elif type == 'double':
            ptr = self.builder.alloca(ir.DoubleType(), name=ident)
        # self.variables[ident] = ptr
        self.scopeStack[-1][ident] = ptr

    def generate_variable_assignment(self, ident, value: GenshinLangParser.ElemToAssignContext):
        # ptr = self.variables.get(ident)
        # print(self.scopeStack[-1])
        ptr = self.scopeStack[-1][ident]
        print(ptr)
        if ptr is None:
            print(f"Zmienna '{ident}' jest niezadeklarowana!")
            sys.exit(1)

        expression_value = self.generate_expression(value.expression())

        if isinstance(self.scopeStack[-1][ident].type.pointee, ir.FloatType):
            expression_value = self._convert_double_to_float(expression_value)
        elif isinstance(self.scopeStack[-1][ident].type.pointee, ir.IntType):
            expression_value = self._convert_double_to_int(expression_value)

        if expression_value is None:
            print(f"Błąd ewaluacji eksprecji '{value}'!")
            sys.exit(1)
        
        self.builder.store(expression_value, ptr)
