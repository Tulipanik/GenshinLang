from llvmlite import ir

class LLVMIOMixin:
    def _declare_print_function(self):
        voidptr_ty = ir.IntType(8).as_pointer()
        printf_ty = ir.FunctionType(ir.IntType(32), [voidptr_ty], var_arg=True)
        self.printf = ir.Function(self.module, printf_ty, name="printf")

        fflush_ty = ir.FunctionType(ir.IntType(32), [self.voidptr_ty])
        self.fflush = ir.Function(self.module, fflush_ty, name="fflush")

    def _declare_scanf_function(self):
        scanf_ty = ir.FunctionType(ir.IntType(32), [self.voidptr_ty], var_arg=True)
        self.scanf = ir.Function(self.module, scanf_ty, name="scanf")

    def _keep_string_in_memory(self, value):
        str_len = len(value) + 1
        
        str_alloca = self.builder.alloca(ir.ArrayType(ir.IntType(8), str_len))

        for i, byte in enumerate(value.encode("utf8") + b"\0"):
            ptr = self.builder.gep(str_alloca, [ir.Constant(ir.IntType(32), 0), ir.Constant(ir.IntType(32), i)])
            self.builder.store(ir.Constant(ir.IntType(8), byte), ptr)
        return str_alloca
    
    def _print_empty_line(self):
        fmt_newline_global = self.module.globals.get("fmt_newline")
        format_ptr = self.builder.gep(fmt_newline_global, [ir.Constant(ir.IntType(32), 0), ir.Constant(ir.IntType(32), 0)])
        self.builder.call(self.printf, [format_ptr])
        self.builder.call(self.fflush, [ir.Constant(ir.IntType(8).as_pointer(), None)])
