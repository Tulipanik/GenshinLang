from llvmlite import ir, binding

class LLVMConfigMixin:
    def _config_llvm(self):
        self.module = ir.Module(name=__file__)
        self.module.triple = self.binding.get_default_triple()
        func_type = ir.FunctionType(ir.IntType(32), [], False)
        main_func = ir.Function(self.module, func_type, name="main")
        block = main_func.append_basic_block(name="entry")
        self.builder = ir.IRBuilder(block)
        self.builder = ir.IRBuilder(block)
        self.voidptr_ty = ir.IntType(8).as_pointer()

        self._declare_format_string()

    def _declare_format_string(self):
        fmt_str = ir.GlobalVariable(self.module, ir.ArrayType(ir.IntType(8), 4), name="fmt_str")
        fmt_str.initializer = ir.Constant(ir.ArrayType(ir.IntType(8), 4), bytearray(b"%s\x20\0"))

        fmt_int_global = ir.GlobalVariable(self.module, ir.ArrayType(ir.IntType(8), 4), name="fmt_int")
        fmt_int_global.initializer = ir.Constant(ir.ArrayType(ir.IntType(8), 4), bytearray(b"%d\x20\0"))

        fmt_float_global = ir.GlobalVariable(self.module, ir.ArrayType(ir.IntType(8), 4), name="fmt_float")
        fmt_float_global.initializer = ir.Constant(ir.ArrayType(ir.IntType(8), 4), bytearray(b"%f\x20\0"))

        fmt_double_global = ir.GlobalVariable(self.module, ir.ArrayType(ir.IntType(8), 5), name="fmt_double")
        fmt_double_global.initializer = ir.Constant(ir.ArrayType(ir.IntType(8), 5), bytearray(b"%lf\x20\0"))

        fmt_newline_global = ir.GlobalVariable(self.module, ir.ArrayType(ir.IntType(8), 2), name="fmt_newline")
        fmt_newline_global.initializer = ir.Constant(ir.ArrayType(ir.IntType(8), 2), bytearray(b"\n\0"))
    
    def _create_execution_engine(self):
        target = self.binding.Target.from_default_triple()
        target_machine = target.create_target_machine()
        backing_mod = binding.parse_assembly("")
        engine = binding.create_mcjit_compiler(backing_mod, target_machine)
        self.engine = engine