# -------------------------------
# Type Checker Implementation
# -------------------------------
from src.parser.parser import ASTNode
from utils.logger import get_logger

logger = get_logger(__name__)
class TypeChecker:
    """Performs semantic analysis and type checking."""
    def __init__(self, ast):
        logger.info("Starting TypeChecker...")
        self.ast = ast
        self.symbol_table = {}  # Stores defined structs and functions

    def check(self):
        """Checks the entire AST for semantic correctness."""
        logger.info("Checking AST...")
        if self.ast.node_type != "Module":
            raise ValueError("Root node must be a Module.")
        # register structs and functions
        for node in self.ast.children:
            if node.node_type == "Struct":
                self.register_struct(node)
            elif node.node_type == "Function":
                self.register_function(node)
        # validate references
        for node in self.ast.children:
            if node.node_type == "Function":
                self.check_function(node)
        logger.debug("Semantic analysis completed.")
        return "Semantic Analysis Passed"

    def register_struct(self, struct_node):
        """Registers struct types in the symbol table."""
        logger.info("Registering struct...")
        struct_name = struct_node.value
        fields = {field.value[0]: field.value[1] for field in struct_node.children}
        self.symbol_table[struct_name] = {"type": "struct", "fields": fields}

    def register_function(self, function_node):
        """Registers function signatures in the symbol table."""
        logger.info("Registering function...")
        func_name = function_node.value
        param_types = {param[0]: param[1] for param in function_node.children[0].value}
        return_type = function_node.children[1].value
        self.symbol_table[func_name] = {
            "type": "function",
            "params": param_types,
            "return": return_type,
        }

    def check_function(self, function_node):
        """Checks if the function's return type and parameters are valid."""
        logger.info("Checking function...")
        func_name = function_node.value
        param_types = self.symbol_table[func_name]["params"]
        return_type = self.symbol_table[func_name]["return"]
        # Validate parameter types
        for param, param_type in param_types.items():
            if param_type not in self.symbol_table and param_type not in [
                "int",
                "float",
                "bool",
                "string",
            ]:
                raise TypeError(
                    f"Undefined type '{param_type}' in parameter '{param}' of function '{func_name}'"
                )
        # Validate return type
        if return_type not in self.symbol_table and return_type not in [
            "int",
            "float",
            "bool",
            "string",
        ]:
            raise TypeError(
                f"Undefined return type '{return_type}' in function '{func_name}'"
            )