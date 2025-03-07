"""
Aegis LLVM IR Code Generator

This module provides LLVM IR generation for the Aegis programming language.
It takes a validated AST and produces LLVM IR using llvmlite.

The generator follows Aegis's deterministic semantics and type safety principles,
optimizing the IR for both JIT execution and AOT compilation.
"""

from llvmlite import ir, binding
from typing import Dict, List, Any, Optional, Union, Tuple
import os
import logging
from utils.logger import get_logger

logger = get_logger(__name__)

# Initialize LLVM
binding.initialize()
binding.initialize_native_target()
binding.initialize_native_asmprinter()

class LLVMGenerator:
    """
    Generates LLVM IR from a validated Aegis AST.
    
    This generator expects a semantically valid AST that has passed type checking.
    It handles all Aegis language constructs, including modules, structs, functions,
    control flow, and expressions.
    
    Attributes:
        ast: The validated AST to generate code from
        module: The LLVM module being generated
        builder: The IRBuilder for creating instructions
        symbol_table: Maps Aegis symbols to their LLVM representations
        current_function: The function currently being generated
    """
    
    def __init__(self, ast: Dict[str, Any], module_name: str = "AegisModule"):
        """
        Initialize the LLVM generator with a validated AST.
        
        Args:
            ast: The validated AST to generate code from
            module_name: The name of the LLVM module to create
        """
        logger.info(f"Initializing LLVM generator for module: {module_name}")
        self.ast = ast
        self.module = ir.Module(name=module_name)
        self.builder = None  # Will be set when generating functions
        self.symbol_table: Dict[str, Dict[str, Any]] = {}
        self.current_function = None
        self.return_values = {}  # For tracking return values in functions
        
        # Add target triple info for the current platform
        # This can be overridden for cross-compilation
        self.module.triple = binding.get_default_triple()
        
        # Initialize standard library declarations
        self._declare_stdlib_functions()
    
    def _declare_stdlib_functions(self):
        """Declare external standard library functions that can be called from Aegis."""
        # Declare C printf for string output
        printf_type = ir.FunctionType(
            ir.IntType(32), [ir.PointerType(ir.IntType(8))], var_arg=True
        )
        printf_func = ir.Function(self.module, printf_type, name="printf")
        self.symbol_table["printf"] = {"value": printf_func, "type": "function"}
        
        # TODO: Add more stdlib functions as needed
    
    def generate(self) -> str:
        """
        Generate LLVM IR for the entire AST.
        
        Returns:
            The generated LLVM IR as a string
        """
        logger.info("Starting LLVM IR generation")
        
        # First pass: declare all types and function signatures
        self._declare_types_and_functions()
        
        # Second pass: implement function bodies
        self._implement_functions()
        
        # Verify the module
        try:
            binding.parse_assembly(str(self.module))
            logger.info("LLVM IR verification successful")
        except Exception as e:
            logger.error(f"LLVM IR verification failed: {e}")
            # Continue anyway, as we want to return the IR even if it has issues
        
        # Return the generated IR
        ir_str = str(self.module)
        logger.debug(f"Generated LLVM IR:\n{ir_str}")
        return ir_str
    
    def _declare_types_and_functions(self):
        """Declare all types (structs, enums) and function signatures."""
        logger.info("Declaring types and function signatures")
        
        # Process top-level module declarations
        if self.ast.get("node_type") == "module":
            self._process_module_declarations(self.ast)
        else:
            # Handle standalone declarations (not in a module)
            for node in self.ast.get("children", []):
                self._declare_node(node)
    
    def _process_module_declarations(self, module_node):
        """Process declarations within a module."""
        module_name = module_node.get("name", "")
        logger.debug(f"Processing declarations in module: {module_name}")
        
        # Create a namespace for this module
        if module_name not in self.symbol_table:
            self.symbol_table[module_name] = {"type": "module", "symbols": {}}
        
        # Process all declarations in the module
        for node in module_node.get("children", []):
            self._declare_node(node, module_name)
    
    def _declare_node(self, node, module_name=None):
        """Declare a node based on its type."""
        node_type = node.get("node_type", "")
        
        if node_type == "struct":
            self._declare_struct(node, module_name)
        elif node_type == "function":
            self._declare_function(node, module_name)
        elif node_type == "module":
            # Handle nested modules
            self._process_module_declarations(node)
    
    def _declare_struct(self, struct_node, module_name=None):
        """
        Declare a struct type in LLVM.
        
        Args:
            struct_node: The AST node for the struct
            module_name: Optional namespace for the struct
        """
        struct_name = struct_node.get("name", "")
        qualified_name = f"{module_name}.{struct_name}" if module_name else struct_name
        logger.debug(f"Declaring struct: {qualified_name}")
        
        # Extract field information
        fields = []
        field_types = []
        
        for field_node in struct_node.get("children", []):
            if field_node.get("node_type") == "field":
                field_name = field_node.get("name", "")
                field_type_str = field_node.get("field_type", {}).get("name", "")
                
                # Get the LLVM type for this field
                field_type = self._get_llvm_type(field_type_str)
                
                fields.append((field_name, field_type))
                field_types.append(field_type)
        
        # Create the LLVM struct type
        struct_type = ir.LiteralStructType(field_types)
        
        # Register the struct in the symbol table
        struct_entry = {
            "type": "struct",
            "llvm_type": struct_type,
            "fields": fields,
        }
        
        if module_name:
            self.symbol_table[module_name]["symbols"][struct_name] = struct_entry
        else:
            self.symbol_table[struct_name] = struct_entry
    
    def _declare_function(self, function_node, module_name=None):
        """
        Declare a function signature in LLVM.
        
        Args:
            function_node: The AST node for the function
            module_name: Optional namespace for the function
        """
        function_name = function_node.get("name", "")
        qualified_name = f"{module_name}.{function_name}" if module_name else function_name
        logger.debug(f"Declaring function: {qualified_name}")
        
        # Extract parameter information
        params = []
        llvm_param_types = []
        
        for param_node in function_node.get("parameters", []):
            param_name = param_node.get("name", "")
            param_type_str = param_node.get("param_type", {}).get("name", "")
            
            # Get the LLVM type for this parameter
            param_type = self._get_llvm_type(param_type_str)
            
            params.append((param_name, param_type))
            llvm_param_types.append(param_type)
        
        # Get the return type
        return_type_node = function_node.get("return_type", {})
        return_type_str = return_type_node.get("name", "void")
        llvm_return_type = self._get_llvm_type(return_type_str)
        
        # Create the function type and declaration
        function_type = ir.FunctionType(llvm_return_type, llvm_param_types)
        function = ir.Function(self.module, function_type, name=qualified_name)
        
        # Name the parameters
        for i, (param_name, _) in enumerate(params):
            function.args[i].name = param_name
        
        # Register the function in the symbol table
        function_entry = {
            "type": "function",
            "value": function,
            "llvm_type": function_type,
            "return_type": return_type_str,
            "params": params,
        }
        
        if module_name:
            self.symbol_table[module_name]["symbols"][function_name] = function_entry
        else:
            self.symbol_table[function_name] = function_entry
    
    def _implement_functions(self):
        """Implement all function bodies."""
        logger.info("Implementing function bodies")
        
        if self.ast.get("node_type") == "module":
            self._implement_module_functions(self.ast)
        else:
            # Handle standalone functions
            for node in self.ast.get("children", []):
                if node.get("node_type") == "function":
                    self._implement_function(node)
    
    def _implement_module_functions(self, module_node):
        """Implement functions within a module."""
        module_name = module_node.get("name", "")
        
        for node in module_node.get("children", []):
            if node.get("node_type") == "function":
                self._implement_function(node, module_name)
            elif node.get("node_type") == "module":
                # Handle nested modules
                self._implement_module_functions(node)
    
    def _implement_function(self, function_node, module_name=None):
        """
        Implement a function body in LLVM.
        
        Args:
            function_node: The AST node for the function
            module_name: Optional namespace for the function
        """
        function_name = function_node.get("name", "")
        qualified_name = f"{module_name}.{function_name}" if module_name else function_name
        logger.debug(f"Implementing function: {qualified_name}")
        
        # Get the function from the symbol table
        function_entry = self.symbol_table.get(qualified_name)
        if not function_entry:
            if module_name:
                function_entry = self.symbol_table.get(module_name, {}).get("symbols", {}).get(function_name)
            
            if not function_entry:
                logger.error(f"Function not found in symbol table: {qualified_name}")
                return
        
        function = function_entry["value"]
        self.current_function = function
        
        # Create the entry basic block
        entry_block = function.append_basic_block(name="entry")
        self.builder = ir.IRBuilder(entry_block)
        
        # Create allocas for parameters at the start of the function
        local_vars = {}
        for i, (param_name, param_type) in enumerate(function_entry["params"]):
            param = function.args[i]
            # Allocate stack space for the parameter
            alloca = self.builder.alloca(param.type, name=param_name)
            # Store the parameter value to the stack
            self.builder.store(param, alloca)
            # Track the variable in our local symbol table
            local_vars[param_name] = {"value": alloca, "type": param_type}
        
        # Create a scope for local variables
        function_scope = {"local_vars": local_vars, "return_type": function_entry["return_type"]}
        
        # Generate code for the function body
        body_nodes = function_node.get("body", [])
        
        # Track if we've seen a return statement
        has_return = False
        
        # Process each statement in the function body
        for stmt_node in body_nodes:
            result = self._generate_statement(stmt_node, function_scope)
            if result and result.get("is_return", False):
                has_return = True
        
        # If no return statement was provided and return type is void, add one
        if not has_return:
            if function_entry["return_type"] == "void":
                self.builder.ret_void()
            else:
                # For non-void functions, provide a default return value based on type
                default_value = self._get_default_value(function_entry["return_type"])
                self.builder.ret(default_value)
        
        # Clean up
        self.current_function = None
        self.builder = None
    
    def _generate_statement(self, stmt_node, scope):
        """
        Generate code for a statement.
        
        Args:
            stmt_node: The AST node for the statement
            scope: The current scope information
            
        Returns:
            A dict with information about the generated statement
        """
        node_type = stmt_node.get("node_type", "")
        
        if node_type == "return_statement":
            return self._generate_return(stmt_node, scope)
        elif node_type == "variable_declaration":
            return self._generate_var_decl(stmt_node, scope)
        elif node_type == "if_statement":
            return self._generate_if(stmt_node, scope)
        elif node_type == "while_statement":
            return self._generate_while(stmt_node, scope)
        elif node_type == "for_statement":
            return self._generate_for(stmt_node, scope)
        elif node_type == "expression_statement":
            return self._generate_expression_stmt(stmt_node, scope)
        else:
            logger.warning(f"Unknown statement type: {node_type}")
            return None
    
    def _generate_return(self, return_node, scope):
        """Generate code for a return statement."""
        logger.debug("Generating return statement")
        
        # Check if there's a value to return
        value_node = return_node.get("value")
        
        if value_node:
            # Generate code for the return value
            value_info = self._generate_expression(value_node, scope)
            if value_info:
                # Add a return instruction
                self.builder.ret(value_info["value"])
        else:
            # No return value (void function)
            self.builder.ret_void()
        
        return {"is_return": True}
    
    def _generate_var_decl(self, var_decl_node, scope):
        """Generate code for a variable declaration."""
        var_name = var_decl_node.get("name", "")
        var_type_str = var_decl_node.get("var_type", {}).get("name", "")
        logger.debug(f"Generating variable declaration: {var_name}: {var_type_str}")
        
        # Get the LLVM type
        var_type = self._get_llvm_type(var_type_str)
        
        # Allocate space for the variable
        alloca = self.builder.alloca(var_type, name=var_name)
        
        # Initialize the variable if there's an initializer
        init_node = var_decl_node.get("init_value")
        if init_node:
            init_info = self._generate_expression(init_node, scope)
            if init_info:
                self.builder.store(init_info["value"], alloca)
        
        # Add the variable to the current scope
        scope["local_vars"][var_name] = {"value": alloca, "type": var_type_str}
        
        return {"var_name": var_name, "var_type": var_type_str}
    
    def _generate_expression_stmt(self, expr_stmt_node, scope):
        """Generate code for an expression statement."""
        expr_node = expr_stmt_node.get("expression")
        if expr_node:
            return self._generate_expression(expr_node, scope)
        return None
    
    def _generate_expression(self, expr_node, scope):
        """
        Generate code for an expression.
        
        Args:
            expr_node: The AST node for the expression
            scope: The current scope information
            
        Returns:
            A dict with information about the generated expression
        """
        node_type = expr_node.get("node_type", "")
        
        if node_type == "binary_operation":
            return self._generate_binary_op(expr_node, scope)
        elif node_type == "unary_operation":
            return self._generate_unary_op(expr_node, scope)
        elif node_type == "literal":
            return self._generate_literal(expr_node)
        elif node_type == "identifier":
            return self._generate_identifier(expr_node, scope)
        elif node_type == "function_call":
            return self._generate_function_call(expr_node, scope)
        elif node_type == "member_access":
            return self._generate_member_access(expr_node, scope)
        else:
            logger.warning(f"Unknown expression type: {node_type}")
            return None
    
    def _generate_literal(self, literal_node):
        """Generate code for a literal value."""
        literal_type = literal_node.get("literal_type", "")
        value = literal_node.get("value")
        
        if literal_type == "int":
            return {
                "value": ir.Constant(ir.IntType(64), value),
                "type": "int",
            }
        elif literal_type == "float":
            return {
                "value": ir.Constant(ir.FloatType(), value),
                "type": "float",
            }
        elif literal_type == "bool":
            return {
                "value": ir.Constant(ir.IntType(1), 1 if value else 0),
                "type": "bool",
            }
        elif literal_type == "string":
            # Create a global constant for the string (including null terminator)
            string_data = bytearray(value, 'utf-8') + bytearray(1)
            string_type = ir.ArrayType(ir.IntType(8), len(string_data))
            global_string = ir.GlobalVariable(self.module, string_type, name=f".str.{hash(value) & 0xFFFFFFFF}")
            global_string.global_constant = True
            global_string.initializer = ir.Constant(string_type, string_data)
            
            # Get a pointer to the string
            zero = ir.Constant(ir.IntType(32), 0)
            string_ptr = self.builder.gep(global_string, [zero, zero], inbounds=True)
            
            return {
                "value": string_ptr,
                "type": "string",
            }
        else:
            logger.warning(f"Unknown literal type: {literal_type}")
            return None
    
    def _generate_identifier(self, identifier_node, scope):
        """Generate code for an identifier reference."""
        name = identifier_node.get("name", "")
        logger.debug(f"Generating identifier reference: {name}")
        
        # Check local variables first
        local_vars = scope.get("local_vars", {})
        if name in local_vars:
            var_info = local_vars[name]
            # Load the value from the alloca
            loaded_value = self.builder.load(var_info["value"], name=f"{name}.load")
            return {
                "value": loaded_value,
                "type": var_info["type"],
            }
        
        # Check global symbols
        if name in self.symbol_table:
            symbol = self.symbol_table[name]
            if symbol["type"] == "function":
                return {
                    "value": symbol["value"],
                    "type": "function",
                }
        
        logger.error(f"Undefined identifier: {name}")
        return None
    
    def _generate_function_call(self, call_node, scope):
        """Generate code for a function call."""
        function_name = call_node.get("name", "")
        logger.debug(f"Generating function call: {function_name}")
        
        # Get the function from the symbol table
        function_entry = self.symbol_table.get(function_name)
        if not function_entry:
            logger.error(f"Function not found: {function_name}")
            return None
        
        function = function_entry["value"]
        
        # Generate code for arguments
        arg_values = []
        for arg_node in call_node.get("arguments", []):
            arg_info = self._generate_expression(arg_node, scope)
            if arg_info:
                arg_values.append(arg_info["value"])
        
        # Call the function
        call_result = self.builder.call(function, arg_values, name=f"{function_name}.call")
        
        return {
            "value": call_result,
            "type": function_entry["return_type"],
        }
    
    def _generate_binary_op(self, binary_op_node, scope):
        """Generate code for a binary operation."""
        operator = binary_op_node.get("operator", "")
        logger.debug(f"Generating binary operation: {operator}")
        
        # Generate code for left and right operands
        left_info = self._generate_expression(binary_op_node.get("left"), scope)
        right_info = self._generate_expression(binary_op_node.get("right"), scope)
        
        if not left_info or not right_info:
            return None
        
        left_value = left_info["value"]
        right_value = right_info["value"]
        left_type = left_info["type"]
        
        # Generate the appropriate instruction based on the operator and types
        if left_type in ["int", "bool"]:
            if operator == "+":
                result = self.builder.add(left_value, right_value, name="add")
            elif operator == "-":
                result = self.builder.sub(left_value, right_value, name="sub")
            elif operator == "*":
                result = self.builder.mul(left_value, right_value, name="mul")
            elif operator == "/":
                result = self.builder.sdiv(left_value, right_value, name="div")
            elif operator == "%":
                result = self.builder.srem(left_value, right_value, name="mod")
            elif operator == "<":
                result = self.builder.icmp_signed("<", left_value, right_value, name="lt")
            elif operator == "<=":
                result = self.builder.icmp_signed("<=", left_value, right_value, name="le")
            elif operator == ">":
                result = self.builder.icmp_signed(">", left_value, right_value, name="gt")
            elif operator == ">=":
                result = self.builder.icmp_signed(">=", left_value, right_value, name="ge")
            elif operator == "==":
                result = self.builder.icmp_signed("==", left_value, right_value, name="eq")
            elif operator == "!=":
                result = self.builder.icmp_signed("!=", left_value, right_value, name="ne")
            elif operator == "&&":
                result = self.builder.and_(left_value, right_value, name="and")
            elif operator == "||":
                result = self.builder.or_(left_value, right_value, name="or")
            else:
                logger.error(f"Unknown integer operator: {operator}")
                return None
        elif left_type == "float":
            if operator == "+":
                result = self.builder.fadd(left_value, right_value, name="add")
            elif operator == "-":
                result = self.builder.fsub(left_value, right_value, name="sub")
            elif operator == "*":
                result = self.builder.fmul(left_value, right_value, name="mul")
            elif operator == "/":
                result = self.builder.fdiv(left_value, right_value, name="div")
            elif operator == "<":
                result = self.builder.fcmp_ordered("<", left_value, right_value, name="lt")
            elif operator == "<=":
                result = self.builder.fcmp_ordered("<=", left_value, right_value, name="le")
            elif operator == ">":
                result = self.builder.fcmp_ordered(">", left_value, right_value, name="gt")
            elif operator == ">=":
                result = self.builder.fcmp_ordered(">=", left_value, right_value, name="ge")
            elif operator == "==":
                result = self.builder.fcmp_ordered("==", left_value, right_value, name="eq")
            elif operator == "!=":
                result = self.builder.fcmp_ordered("!=", left_value, right_value, name="ne")
            else:
                logger.error(f"Unknown float operator: {operator}")
                return None
        else:
            logger.error(f"Unsupported type for binary operation: {left_type}")
            return None
        
        # Determine the result type
        if operator in ["<", "<=", ">", ">=", "==", "!="]:
            return {
                "value": result,
                "type": "bool",
            }
        else:
            return {
                "value": result,
                "type": left_type,
            }
    
    def _generate_unary_op(self, unary_op_node, scope):
        """Generate code for a unary operation."""
        operator = unary_op_node.get("operator", "")
        logger.debug(f"Generating unary operation: {operator}")
        
        # Generate code for the operand
        operand_info = self._generate_expression(unary_op_node.get("operand"), scope)
        
        if not operand_info:
            return None
        
        operand_value = operand_info["value"]
        operand_type = operand_info["type"]
        
        # Generate the appropriate instruction based on the operator and type
        if operator == "-":
            if operand_type == "int":
                result = self.builder.neg(operand_value, name="neg")
            elif operand_type == "float":
                result = self.builder.fneg(operand_value, name="fneg")
            else:
                logger.error(f"Unsupported type for negation: {operand_type}")
                return None
        elif operator == "!":
            if operand_type == "bool":
                result = self.builder.not_(operand_value, name="not")
            else:
                logger.error(f"Unsupported type for logical not: {operand_type}")
                return None
        else:
            logger.error(f"Unknown unary operator: {operator}")
            return None
        
        return {
            "value": result,
            "type": operand_type,
        }
    
    def _get_llvm_type(self, aegis_type_str):
        """
        Get the LLVM type corresponding to an Aegis type.
        
        Args:
            aegis_type_str: The Aegis type name
            
        Returns:
            The corresponding LLVM type
        """
        if aegis_type_str == "int":
            return ir.IntType(64)
        elif aegis_type_str == "float":
            return ir.FloatType()
        elif aegis_type_str == "bool":
            return ir.IntType(1)
        elif aegis_type_str == "string":
            return ir.PointerType(ir.IntType(8))
        elif aegis_type_str == "void":
            return ir.VoidType()
        else:
            # Check if it's a struct type
            if aegis_type_str in self.symbol_table:
                struct_entry = self.symbol_table[aegis_type_str]
                if struct_entry["type"] == "struct":
                    return struct_entry["llvm_type"]
            
            logger.warning(f"Unknown type: {aegis_type_str}, defaulting to void")
            return ir.VoidType()
    
    def _get_default_value(self, aegis_type_str):
        """Get a default value for a given Aegis type."""
        if aegis_type_str == "int":
            return ir.Constant(ir.IntType(64), 0)
        elif aegis_type_str == "float":
            return ir.Constant(ir.FloatType(), 0.0)
        elif aegis_type_str == "bool":
            return ir.Constant(ir.IntType(1), 0)
        elif aegis_type_str == "string":
            # Return empty string
            string_data = bytearray(1)  # Just the null terminator
            string_type = ir.ArrayType(ir.IntType(8), 1)
            global_string = ir.GlobalVariable(self.module, string_type, name=f".str.empty")
            global_string.global_constant = True
            global_string.initializer = ir.Constant(string_type, string_data)
            
            # Get a pointer to the string
            zero = ir.Constant(ir.IntType(32), 0)
            return self.builder.gep(global_string, [zero, zero], inbounds=True)
        else:
            # For custom types, return null pointer
            llvm_type = self._get_llvm_type(aegis_type_str)
            if isinstance(llvm_type, ir.PointerType):
                return ir.Constant(llvm_type, None)
            else:
                logger.warning(f"No default value for type: {aegis_type_str}")
                return ir.Constant(ir.IntType(64), 0)

# WebAssembly Support
class WasmGenerator(LLVMGenerator):
    """
    Extends the LLVM Generator to produce WebAssembly-compatible IR.
    
    This class overrides key methods to ensure the generated IR complies
    with WebAssembly's more limited type system and memory model.
    """
    
    def __init__(self, ast: Dict[str, Any], module_name: str = "AegisWasmModule"):
        """Initialize the WebAssembly generator."""
        super().__init__(ast, module_name)
        
        # Set the WebAssembly target triple
        self.module.triple = "wasm32-unknown-unknown"
    
    def _get_llvm_type(self, aegis_type_str):
        """Get WebAssembly-compatible LLVM types."""
        if aegis_type_str == "int":
            # WebAssembly prefers 32-bit integers
            return ir.IntType(32)
        else:
            # Use the parent implementation for other types
            return super()._get_llvm_type(aegis_type_str)
    
    def _declare_stdlib_functions(self):
        """Declare WebAssembly-compatible stdlib functions."""
        # In WebAssembly, we'd use imports for standard library functions
        # This is a simplified example - actual WASM exports would need more configuration
        
        # Declare console_log for string output in WebAssembly
        console_log_type = ir.FunctionType(
            ir.VoidType(), [ir.PointerType(ir.IntType(8))]
        )
        console_log = ir.Function(self.module, console_log_type, name="console_log")
        self.symbol_table["console_log"] = {"value": console_log, "type": "function"}

# Example function showing how to generate LLVM IR for a function
def example_function_ir_generation():
    """Example of generating LLVM IR for a simple function."""
    module = ir.Module(name="example")
    
    # Define a function that adds two integers
    func_type = ir.FunctionType(ir.IntType(64), [ir.IntType(64), ir.IntType(64)])
    func = ir.Function(module, func_type, name="add")
    
    # Name the parameters
    func.args[0].name = "a"
    func.args[1].name = "b"
    
    # Create a basic block
    block = func.append_basic_block(name="entry")
    builder = ir.IRBuilder(block)
    
    # Add the parameters
    result = builder.add(func.args[0], func.args[1], name="result")
    
    # Return the result
    builder.ret(result)
    
    # Print the IR
    print(str(module))
    return str(module)

if __name__ == "__main__":
    # Example usage
    print("LLVM IR example for a simple function:")
    print(example_function_ir_generation())