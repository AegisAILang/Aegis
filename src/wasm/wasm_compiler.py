from llvmlite import ir


# Enabling Compilation to WebAssembly (WASM) for AegisLang
class WebAssemblyCompiler:
    """Compiles AegisLang LLVM IR into WebAssembly (WASM) bytecode."""

    def __init__(self, llvm_ir):
        self.llvm_ir = llvm_ir

    def compile_to_wasm(self):
        """Compiles the LLVM IR to WASM."""
        # Create a WASM-compatible target machine
        target_triple = "wasm32-unknown-unknown"
        target = binding.Target.from_triple(target_triple)
        target_machine = target.create_target_machine(codemodel="default")

        # Convert LLVM IR to WASM binary format
        llvm_module = binding.parse_assembly(self.llvm_ir)
        llvm_module.verify()

        object_code = target_machine.emit_object(llvm_module)

        # Save the compiled WASM file
        wasm_filename = "output.wasm"
        with open(wasm_filename, "wb") as wasm_file:
            wasm_file.write(object_code)

        return f"WebAssembly compilation successful. Output saved as '{wasm_filename}'."


# Generating WebAssembly-Compatible LLVM IR


class WebAssemblyIRGenerator(CodeGenerator):
    """Generates WebAssembly-compatible LLVM IR for AegisLang."""

    def __init__(self, ast):
        super().__init__(ast)
        self.module.triple = "wasm32-unknown-unknown"

    def generate_function(self, function_node):
        """Generates WASM-compatible LLVM function definitions."""
        func_name = function_node.value
        param_list = function_node.children[0].value  # [(param_name, param_type), ...]
        return_type = function_node.children[1].value

        # Convert function types (WASM supports only specific types)
        llvm_return_type = self.get_wasm_compatible_type(return_type)
        llvm_param_types = [
            self.get_wasm_compatible_type(ptype) for _, ptype in param_list
        ]

        # Create function signature
        func_type = ir.FunctionType(llvm_return_type, llvm_param_types)
        func = ir.Function(self.module, func_type, name=func_name)

        # Register in symbol table
        self.symbol_table[func_name] = func

    def get_wasm_compatible_type(self, aegis_type):
        """Maps AegisLang types to WASM-compatible LLVM types."""
        wasm_type_map = {
            "int": ir.IntType(32),  # WebAssembly prefers 32-bit integers
            "float": ir.FloatType(),
            "bool": ir.IntType(1),
            "string": ir.PointerType(
                ir.IntType(8)
            ),  # WASM handles strings as memory pointers
        }
        return wasm_type_map.get(
            aegis_type, ir.VoidType()
        )  # Default to void if unknown
