import sys
from llvmlite import ir
from generated.GenshinLangParser import GenshinLangParser

class LLVMVariablesMixin:
    def generate_variable_declaration(self, ident, type):
        if type == 'int':
            ptr = self.builder.alloca(ir.IntType(32), name=ident)
        elif type == 'float':
            ptr = self.builder.alloca(ir.FloatType(), name=ident)
        elif type == 'double' or type == 'var':
            ptr = self.builder.alloca(ir.DoubleType(), name=ident)
        self.scopeStack[-1][ident] = ptr

    def generate_global_variable_declaration(self, ident, type):
        var_type = ir.IntType(32)

        if type == 'int':
            var_type = ir.IntType(32)
        elif type == 'float':
            var_type = ir.FloatType()
        elif type == 'double' or type == 'var':
            var_type = ir.DoubleType()


        global_var = ir.GlobalVariable(self.module, var_type, name=ident)
        global_var.initializer = ir.Constant(var_type, 0)
        global_var.global_constant = False

        self.global_scope[ident] = global_var

    def generate_variable_assignment(self, ident, value: GenshinLangParser.ElemToAssignContext):
        ptr = None
        idx = len(self.scopeStack) - 1

        while not(idx == -1):
            ptr = ident in self.scopeStack[idx]
            if ptr:
                ptr = self.scopeStack[idx][ident]
                break

            idx -= 1
            
        if not(ptr):
            if ident in self.global_scope:
                ptr = self.global_scope[ident]
            else:  
                print(f"Przypisanie do niezadeklarowanej zmiennej '{ident}'!")
                sys.exit(1)

        expression_value = self.generate_expression(value.expression())

        if isinstance(ptr.type.pointee, ir.FloatType):
            expression_value = self._convert_double_to_float(expression_value)
        elif isinstance(ptr.type.pointee, ir.IntType):
            expression_value = self._convert_double_to_int(expression_value)

        if expression_value is None:
            print(f"Błąd ewaluacji ekspresji '{value}'!")
            sys.exit(1)
        
        self.builder.store(expression_value, ptr)

    
    def generate_short_variable_assignment(self, ident, value):
        ptr = None
        idx = len(self.scopeStack) - 1

        while not(idx == -1):
            ptr = ident in self.scopeStack[idx]
            if ptr:
                ptr = self.scopeStack[idx][ident]
                break

            idx -= 1

        if not(ptr):
            if ident in self.global_scope:
                ptr = self.global_scope[ident]
            else:
                print(f"Przypisanie do niezadeklarowanej zmiennej '{ident}'!")
                sys.exit(1)

        if isinstance(ptr.type.pointee, ir.FloatType):
            value = self._convert_double_to_float(value)
        elif isinstance(ptr.type.pointee, ir.IntType):
            value = self._convert_double_to_int(value)

        if value is None:
            print(f"Błąd ewaluacji ekspresji '{value}'!")
            sys.exit(1)
        
        self.builder.store(value, ptr)