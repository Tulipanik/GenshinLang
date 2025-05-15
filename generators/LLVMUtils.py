import sys
from llvmlite import ir

class LLVMUtilsMixin:
    def _load_variable(self, ident):
        ptr = None
        idx = len(self.scopeStack) - 1

        while not(idx == -1):
            ptr = ident in self.scopeStack[idx]

            if ptr:
                ptr = self.scopeStack[idx][ident]
                break

            idx -= 1

        if not(ptr):
            if ident not in self.global_scope:
                print(f"Zmienna '{ident}' użyta przed zadeklarowaniem!")
                sys.exit(-1)
            else:
                ptr = self.global_scope[ident]

        return self.builder.load(ptr)

    def _check_type_compability(self, value1, value2):
        type1 = value1.type
        type2 = value2.type

        if type1 == type2:
            return value1, value2

        if isinstance(type1, ir.IntType) and isinstance(type2, (ir.FloatType, ir.DoubleType)):
            return self._convert_int_to_float(value1, type2), value2

        if isinstance(type2, ir.IntType) and isinstance(type1, (ir.FloatType, ir.DoubleType)):
            return value1, self._convert_int_to_float(value2, type1)

        if isinstance(type1, ir.FloatType) and isinstance(type2, ir.DoubleType):
            return self._convert_float_to_double(value1), value2

        if isinstance(type1, ir.DoubleType) and isinstance(type2, ir.FloatType):
            return value1, self._convert_float_to_double(value2)

        if isinstance(type1, (ir.FloatType, ir.DoubleType)) and isinstance(type2, (ir.FloatType, ir.DoubleType)):
            if isinstance(type1, ir.FloatType):
                return self._convert_float_to_double(value1), value2
            else:
                return value1, self._convert_float_to_double(value2)

        return value1, value2

    def _convert_int_to_float(self, value, dest_type):
        if isinstance(value.type, ir.IntType):
            if dest_type == ir.FloatType():
                return self.builder.sitofp(value, ir.FloatType())
            elif dest_type == ir.DoubleType():
                return self.builder.sitofp(value, ir.DoubleType())
        return value

    def _convert_float_to_double(self, value):
        if isinstance(value.type, ir.FloatType):
            return self.builder.fpext(value, ir.DoubleType())
        return value
    
    def _convert_double_to_float(self, value):
        return self.builder.fptrunc(value, ir.FloatType())
    
    def _convert_double_to_int(self, value):
        return self.builder.fptosi(value, ir.IntType(32))