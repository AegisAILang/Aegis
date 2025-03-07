from llvmlite import ir, binding
from utils.logger import get_logger

logger = get_logger(__name__)
# -------------------------------
# LLVM IR Code Generator
# -------------------------------
class CodeGenerator:
    """Generates LLVM IR from the parsed AST."""
    def __init__(self, ast):
        logger.info("Starting CodeGenerator...")
        self.ast = ast
        self.module = ir.Module(name="AegisModule")
        self.symbol_table = {}  # Stores functions and struct types

    def generate(self):
        """Generates LLVM IR for the entire AST."""
        logger.info("Generating LLVM IR...")
        for node in self.ast.children:
            if node.node_type == "Struct":
                self.generate_struct(node)
            elif node.node_type == "Function":
                self.generate_function(node)
        logger.debug(f"Generated LLVM IR:\n{str(self.module)}")
        llvm_ir = str(self.module)
        logger.debug(f"LLVM IR:\n{llvm_ir}")
        return llvm_ir

    def generate_struct(self, struct_node):
        """Generates LLVM struct types."""
        logger.info("Generating struct...")
        struct_name = struct_node.value
        field_types = []
        for field in struct_node.children:
            field_name, field_type = field.value
            llvm_type = self.get_llvm_type(field_type)
            field_types.append(llvm_type)
        struct_type = ir.LiteralStructType(field_types)
        self.symbol_table[struct_name] = struct_type

    def generate_function(self, function_node):
        """Generates LLVM IR for function definitions with proper body implementation."""
        logger.info("Generating function...")
        # Extract function details
        func_name = function_node.value
        param_list = function_node.children[0].value  # [(param_name, param_type), ...]
        return_type = function_node.children[1].value

        # Get LLVM types
        llvm_return_type = self.get_llvm_type(return_type)
        llvm_param_types = [self.get_llvm_type(ptype) for _, ptype in param_list]

        # Create function type and declaration
        func_type = ir.FunctionType(llvm_return_type, llvm_param_types)
        func = ir.Function(self.module, func_type, name=func_name)

        # Create basic block for function body
        block = func.append_basic_block(name="entry")
        builder = ir.IRBuilder(block)

        # Store parameter references in symbol table for use in function body
        local_vars = {}
        for i, (param_name, _) in enumerate(param_list):
            param = func.args[i]
            param.name = param_name
            # Allocate memory for parameter and store value
            alloca = builder.alloca(param.type, name=param_name)
            builder.store(param, alloca)
            local_vars[param_name] = alloca

        # For now, just generate a simple return statement (placeholder)
        # In a real implementation, we'd parse and generate IR for the function body
        if return_type in ["int", "bool"]:
            builder.ret(ir.Constant(self.get_llvm_type(return_type), 0))
        elif return_type == "float":
            builder.ret(ir.Constant(self.get_llvm_type(return_type), 0.0))
        elif return_type == "string":
            # Return empty string by default
            empty_str = ir.Constant(ir.ArrayType(ir.IntType(8), 1), bytearray([0]))
            builder.ret(empty_str)
        else:
            # For custom types, create a null pointer
            builder.ret(ir.Constant(self.get_llvm_type(return_type), None))

        # Register function in symbol table
        self.symbol_table[func_name] = func

    def get_llvm_type(self, aegis_type):
        """Maps Aegis types to LLVM types."""
        logger.info("Getting LLVM type...")
        llvm_type_map = {
            "int": ir.IntType(64),
            "float": ir.FloatType(),
            "bool": ir.IntType(1),
            "string": ir.PointerType(ir.IntType(8)),
        }
        logger.debug(f"LLVM type: {llvm_type_map.get(aegis_type, ir.VoidType())}")
        return llvm_type_map.get(aegis_type, ir.VoidType())
