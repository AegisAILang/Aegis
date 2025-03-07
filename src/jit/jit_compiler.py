import os
import ctypes
from llvmlite import ir, binding
from utils.logger import get_logger

logger = get_logger(__name__)
# -------------------------------
# JIT Compiler
# -------------------------------
# init LLVM
logger.info("Initializing LLVM...")
binding.initialize()
binding.initialize_native_target()
binding.initialize_native_asmprinter()

# Load native library (assuming libaegis_stdimpl.dylib is in ./build)
lib_path = os.path.join(
    os.path.dirname(__file__), "..", "build", "libaegis_stdimpl.dylib"
)
if os.path.exists(lib_path):
    binding.load_library_permanently(lib_path)
else:
    raise FileNotFoundError(f"Native library not found at {lib_path}")


class JITCompiler:
    """Just-In-Time compiler for executing LLVM IR."""
    def __init__(self, llvm_ir):
        """Initialize with generated LLVM IR."""
        logger.info("Initializing JITCompiler...")
        self.llvm_ir = llvm_ir
        self.target = binding.Target.from_default_triple()
        self.target_machine = self.target.create_target_machine()
        self.backing_mod = binding.parse_assembly("")
        self.engine = binding.create_mcjit_compiler(
            self.backing_mod, self.target_machine
        )

    def compile_and_execute(self):
        """Compile and execute the LLVM IR."""
        logger.info("Compiling and executing LLVM IR...")
        try:
            # Parse the IR
            mod = binding.parse_assembly(self.llvm_ir)
            mod.verify()
            # Add the module and make sure it's ready for execution
            self.engine.add_module(mod)
            self.engine.finalize_object()

            # Look up the main function if it exists
            try:
                main_func_ptr = self.engine.get_function_address("main")
                main_func = ctypes.CFUNCTYPE(ctypes.c_int)(main_func_ptr)
                result = main_func()
                return f"Execution complete. Main function returned: {result}"
            except NameError:
                # Find any function to execute as demo
                for func in mod.functions:
                    if not func.is_declaration:
                        func_ptr = self.engine.get_function_address(func.name)
                        # Get the return type and param types
                        return_type = self._get_ctype_for_func_return(func)
                        param_types = [
                            self._get_ctype_for_type(param.type) for param in func.args
                        ]
                        # Create a callable function
                        func_type = ctypes.CFUNCTYPE(return_type, *param_types)
                        callable_func = func_type(func_ptr)
                        # Execute with default values
                        default_args = [
                            self._get_default_value(param.type) for param in func.args
                        ]
                        result = callable_func(*default_args)
                        logger.debug(f"Executed function '{func.name}' with result: {result}")
                        return f"Executed function '{func.name}' with result: {result}"
                    else:
                        logger.warning(f"Skipping declaration for function '{func.name}'")
                return "No executable functions found in the module."

        except Exception as e:
            logger.error(f"Error during compilation or execution: {str(e)}")
            return f"Error during compilation or execution: {str(e)}"

    def _get_ctype_for_type(self, llvm_type):
        """Map LLVM types to ctypes types."""
        logger.info("Getting ctypes type...")
        if llvm_type.is_integer():
            if llvm_type.width <= 8:
                return ctypes.c_uint8
            elif llvm_type.width <= 16:
                return ctypes.c_uint16
            elif llvm_type.width <= 32:
                return ctypes.c_uint32
            else:
                return ctypes.c_uint64
        elif llvm_type.is_float():
            return ctypes.c_float
        elif llvm_type.is_double():
            return ctypes.c_double
        elif llvm_type.is_pointer():
            return ctypes.c_void_p
        else:
            # Default to void pointer for complex types
            logger.warning("Defaulting to void pointer for complex types")
            return ctypes.c_void_p

    def _get_ctype_for_func_return(self, func):
        """Get the ctypes return type for a function."""
        logger.info("Getting ctypes return type...")
        return_type = func.return_type
        if str(return_type) == "void":
            return None
        logger.debug(f"Ctypes return type: {self._get_ctype_for_type(return_type)}")
        return self._get_ctype_for_type(return_type)

    def _get_default_value(self, llvm_type):
        """Get a default value for a given LLVM type."""
        logger.info("Getting default value...")
        if llvm_type.is_integer():
            logger.debug("Defaulting to 0 for integer")
            return 0
        elif llvm_type.is_float() or llvm_type.is_double():
            logger.debug("Defaulting to 0.0 for float or double")
            return 0.0
        elif llvm_type.is_pointer():
            logger.warning("Defaulting to None for pointer types")
            return None
        else:
            logger.warning("Defaulting to None for complex types")
            return None
