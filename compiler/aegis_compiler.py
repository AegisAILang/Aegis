"""
AegisLang Compiler
This file implements the Lexer, Parser, Type Checker, LLVM IR Generator, and JIT Compiler.
"""

## lex → parse → type-check → generate IR → JIT execute.

import os
import re
import sys
import time
import ctypes
from llvmlite import ir, binding
from utils.logger import get_logger

logger = get_logger(__name__)
# -------------------------------
# Lexer Implementation
# -------------------------------
# Token definitions: keywords, types, operators, symbols.
# A lex() function that scans the source code and returns tokens.
TOKEN_TYPES = {
    "KEYWORDS": [
        "fn",
        "struct",
        "enum",
        "return",
        "if",
        "else",
        "elif",
        "for",
        "while",
        "module",
        "let",
        "mut",
        "async",
        "await",
        "task",
    ],
    "TYPES": [
        "int",
        "float",
        "bool",
        "char",
        "string",
        "List",
        "Array",
        "Map",
        "Option",
        "Result",
    ],
    "OPERATORS": [
        "+",
        "-",
        "*",
        "/",
        "=",
        "==",
        "!=",
        ">=",
        "<=",
        "<",
        ">",
        "->",
        "::",
    ],
    "SYMBOLS": [":", ",", "(", ")", "[", "]", "{", "}", "...", "parallel"],
}

TOKEN_PATTERNS = [
    (
        r"\b(fn|struct|enum|return|if|else|elif|for|while|module|let|mut|async|await|task)\b",
        "KEYWORD",
    ),
    (r"\b(int|float|bool|char|string|List|Array|Map|Option|Result)\b", "TYPE"),
    (r"\b[0-9]+\b", "NUMBER"),
    (r"\b[a-zA-Z_][a-zA-Z0-9_]*\b", "IDENTIFIER"),
    (r'".*?"', "STRING"),
    (r"#[^\n]*", "COMMENT"),
    (r"[\+\-\*/=<>!:]+", "OPERATOR"),
    (r"[\(\)\[\]\{\},:]", "SYMBOL"),
    (r"\s+", None),  # Ignore whitespace
]


# -------------------------------
# Lexer Function
# -------------------------------
def lex(input_code):
    """Enhanced lexer with better error handling and context."""
    logger.info("Starting lexer...")
    tokens = []
    line_num = 1
    column = 1
    input_len = len(input_code)
    idx = 0

    while idx < input_len:
        match_found = False

        # Track line numbers
        if input_code[idx] == "\n":
            line_num += 1
            column = 1
            idx += 1
            continue

        for pattern, token_type in TOKEN_PATTERNS:
            match = re.match(pattern, input_code[idx:])
            if match:
                if token_type:  # Skip whitespace
                    tokens.append((token_type, match.group(0), line_num, column))
                    logger.debug(f"Token: {token_type}, {match.group(0)}, {line_num}, {column}")
                idx += len(match.group(0))
                column += len(match.group(0))
                match_found = True
                break

        if not match_found:
            logger.error(f"No match found for line {line_num}, column {column}")
            # Extract a snippet of the problematic code for context
            context_start = max(0, idx - 10)
            context_end = min(len(input_code), idx + 10)
            context = input_code[context_start:context_end]
            position_marker = " " * (min(10, idx - context_start)) + "^"

            error_msg = (
                f"Lexical error at line {line_num}, column {column}:\n"
                f"{context}\n{position_marker}\n"
                f"Unexpected character: '{input_code[idx]}'"
            )
            raise SyntaxError(error_msg)
    logger.debug(f"Lexer tokens: {len(tokens)} tokens.")
    logger.info("Lexer completed successfully.")
    return tokens


# Lexing with indentation (if you want indentation-based blocks).
# By default, you don't need this for your current grammar. If you keep it, define `lex_line`.
def lex_line(line_content, line_num):
    """
    A helper to tokenize a single line (used by lex_with_indentation).
    Mirrors the `lex` logic but for one line.
    """
    logger.info("Starting lex_line...")
    tokens = []
    idx = 0
    column = 1
    length = len(line_content)

    while idx < length:
        match_found = False
        if line_content[idx] == "\n":
            # not strictly needed here
            idx += 1
            column = 1
            continue

        for pattern, token_type in TOKEN_PATTERNS:
            match = re.match(pattern, line_content[idx:])
            if match:
                if token_type:
                    tokens.append((token_type, match.group(0), line_num, column))
                idx += len(match.group(0))
                column += len(match.group(0))
                match_found = True
                break

        if not match_found:
            logger.error(f"No match found for line {line_num}, column {column}")
            context_start = max(0, idx - 10)
            context_end = min(length, idx + 10)
            context = line_content[context_start:context_end]
            position_marker = " " * (min(10, idx - context_start)) + "^"

            error_msg = (
                f"Lexical error at line {line_num}, column {column}:\n"
                f"{context}\n{position_marker}\n"
                f"Unexpected character: '{line_content[idx]}'"
            )
            raise SyntaxError(error_msg)
    logger.debug(f"Lexed line {line_num}: {tokens}")
    return tokens


def lex_with_indentation(input_code):
    """Lexer that handles indentation levels for scoping."""
    logger.info("Starting lex_with_indentation...")
    tokens = []
    lines = input_code.splitlines()

    # Track indentation stack
    indent_stack = [0]  # Start with 0 indentation

    for line_num, line in enumerate(lines, 1):
        # Skip empty lines
        if not line.strip():
            continue

        # Calculate indentation level
        indent = len(line) - len(line.lstrip())
        line_content = line.lstrip()

        # Skip comment-only lines
        if line_content.startswith("#"):
            continue

        # Handle indentation changes
        if indent > indent_stack[-1]:
            # Indentation increased - push new level and emit INDENT token
            indent_stack.append(indent)
            tokens.append(("INDENT", "", line_num, 0))
        elif indent < indent_stack[-1]:
            # Indentation decreased - pop levels and emit DEDENT tokens
            while indent < indent_stack[-1]:
                indent_stack.pop()
                tokens.append(("DEDENT", "", line_num, 0))

            # Ensure indent level matches exactly one of the previous levels
            if indent != indent_stack[-1]:
                # invalid indent
                raise IndentationError(
                    f"Line {line_num}: Invalid indentation level (got {indent}, expected {indent_stack[-1]})"
                )

        # Now lex the actual content of the line
        line_tokens = lex_line(line_content, line_num)
        tokens.extend(line_tokens)

        # Add implicit line end
        tokens.append(("NEWLINE", "\n", line_num, len(line)))

    # Add any remaining DEDENT tokens at the end of the file
    while len(indent_stack) > 1:
        indent_stack.pop()
        tokens.append(("DEDENT", "", len(lines) + 1, 0))

    logger.debug(f"Lexed with indentation: {tokens}")
    return tokens


# -------------------------------
# Parser Implementation
# -------------------------------
# A TokenStream class to manage tokens.
# An ASTNode class to build the abstract syntax tree.
# An AegisParser that produces the AST from tokens.
class TokenStream:
    """A simple stream to process tokens sequentially."""
    def __init__(self, tokens):
        logger.info("Starting TokenStream...")
        self.tokens = tokens
        self.index = 0

    def peek(self):
        """Returns the current token without consuming it."""
        logger.debug(f"Peeking token: {self.tokens[self.index]}")
        if self.index < len(self.tokens):
            return self.tokens[self.index]
        logger.warning("No more tokens to peek.")
        return None

    def consume(self):
        """Consumes the current token and moves to the next."""
        logger.info("Consuming token...")
        token = self.peek()
        self.index += 1
        logger.debug(f"Consumed token: {token}")
        return token

    def expect(self, expected_type):
        """Consumes and verifies a token type."""
        logger.info("Expecting token...")
        token = self.consume()
        if token is None or token[0] != expected_type:
            raise SyntaxError(f"Expected {expected_type}, but got {token}")
        logger.debug(f"Expected token: {token}")
        return token


class ASTNode:
    """Base class for AST nodes."""
    def __init__(self, node_type, value=None):
        logger.info("Initializing ASTNode...")
        self.node_type = node_type
        self.value = value
        self.children = []
    def add_child(self, child):
        self.children.append(child)
    def __repr__(self):
        logger.debug(f"ASTNode: {self.node_type}({self.value}, children={self.children})")
        return f"{self.node_type}({self.value}, children={self.children})"


class AegisParser:
    """Enhanced parser with improved error handling."""
    def __init__(self, tokens):
        logger.info("Initializing AegisParser...")
        self.tokens = TokenStream(tokens)

    def parse_module(self):
        """Parses a module declaration."""
        logger.info("Parsing module...")
        self.tokens.expect("KEYWORD")  # "module"
        module_name = self.tokens.expect("IDENTIFIER")[1]
        self.tokens.expect("SYMBOL")  # ":" correctly defined as SYMBOL
        module_node = ASTNode("Module", module_name)
        logger.debug(f"Module parsed with name: {module_name}")

        # parse children
        while self.tokens.peek() and self.tokens.peek()[0] == "KEYWORD":
            keyword = self.tokens.peek()[1]
            if keyword == "struct":
                module_node.add_child(self.parse_struct())
            elif keyword == "fn":
                module_node.add_child(self.parse_function())
            else:
                break
        logger.debug(f"Parsed module: {module_node}")
        return module_node

    def parse_struct(self):
        """Parses a struct declaration."""  
        logger.info("Parsing struct...")
        self.tokens.expect("KEYWORD")  # "struct"
        struct_name = self.tokens.expect("IDENTIFIER")[1]
        self.tokens.expect("OPERATOR")  # ":"
        struct_node = ASTNode("Struct", struct_name)

        # parse fields
        while self.tokens.peek() and self.tokens.peek()[0] == "IDENTIFIER":
            field_name = self.tokens.expect("IDENTIFIER")[1]
            self.tokens.expect("OPERATOR")  # ":"
            field_type = self.tokens.expect("TYPE")[1]
            struct_node.add_child(ASTNode("Field", (field_name, field_type)))
        logger.debug(f"Parsed struct: {struct_node}")
        return struct_node

    def parse_function(self):
        """Parses a function declaration."""
        logger.info("Parsing function...")
        """fn <Name>(<Params>) -> <ReturnType>"""
        self.tokens.expect("KEYWORD")  # "fn"
        function_name = self.tokens.expect("IDENTIFIER")[1]
        self.tokens.expect("SYMBOL")  # "("
        params = []
        # parse params
        while self.tokens.peek() and self.tokens.peek()[0] == "IDENTIFIER":
            param_name = self.tokens.expect("IDENTIFIER")[1]
            self.tokens.expect("OPERATOR")  # ":"
            token = self.tokens.peek()
            if token[0] == "TYPE":
                param_type = self.tokens.expect("TYPE")[1]
            else:
                # user-defined type
                param_type = self.tokens.expect("IDENTIFIER")[1]
            params.append((param_name, param_type))
            if self.tokens.peek() and self.tokens.peek()[0] == "SYMBOL":
                if self.tokens.peek()[1] == ")":
                    break
                self.tokens.expect("SYMBOL")  # ","
        self.tokens.expect("SYMBOL")  # ")"
        self.tokens.expect("OPERATOR")  # "->"
        # Allow both built-in types and user-defined types
        token = self.tokens.peek()
        if token[0] == "TYPE":
            return_type = self.tokens.expect("TYPE")[1]
        else:
            return_type = self.tokens.expect("IDENTIFIER")[1]
        self.tokens.expect("OPERATOR")  # ":"
        func_node = ASTNode("Function", function_name)
        func_node.add_child(ASTNode("Parameters", params))
        func_node.add_child(ASTNode("ReturnType", return_type))
        logger.debug(f"Parsed function: {func_node}")
        return func_node

    def parse_block(self):
        """Parse an indentation-based block."""
        logger.info("Parsing block...")
        self.tokens.expect("INDENT", context="block")
        block_nodes = []
        while self.tokens.peek() and self.tokens.peek()[0] != "DEDENT":
            # Parse statements in the block
            if self.tokens.peek()[0] == "KEYWORD":
                keyword = self.tokens.peek()[1]
                if keyword == "if":
                    block_nodes.append(self.parse_if_statement())
                elif keyword == "while":
                    block_nodes.append(self.parse_while_statement())
                elif keyword == "return":
                    block_nodes.append(self.parse_return_statement())
                # Add other statement types as needed
            elif self.tokens.peek()[0] == "IDENTIFIER":
                block_nodes.append(self.parse_expression_statement())

            # Expect a newline after each statement
            self.tokens.expect("NEWLINE", context="statement")
        self.tokens.expect("DEDENT", context="end of block")
        logger.debug(f"Parsed block: {block_nodes}")
        return block_nodes

    def parse_if_statement(self):
        logger.warning("parse_if_statement not implemented yet.")
        pass  # TODO: implement

    def parse_while_statement(self):
        logger.warning("parse_while_statement not implemented yet.")
        pass  # TODO: implement

    def parse_return_statement(self):
        logger.warning("parse_return_statement not implemented yet.")
        pass  # TODO: implement

    def parse(self):
        """Parses the entire code into an AST."""
        logger.info("Parsing entire code...")
        return self.parse_module()

    def expect(self, expected_type, context=None):
        """Expects a token of a specific type with improved error messages."""
        logger.info("Expecting token...")
        token = self.tokens.consume()
        if token is None:
            context_msg = f" while parsing {context}" if context else ""
            raise SyntaxError(
                f"Unexpected end of file{context_msg}. Expected {expected_type}."
            )

        if token[0] != expected_type:
            line = token[2] if len(token) > 2 else "unknown"
            column = token[3] if len(token) > 3 else "unknown"
            context_msg = f" while parsing {context}" if context else ""

            raise SyntaxError(
                f"Line {line}, column {column}{context_msg}: "
                f"Expected {expected_type}, but got {token[0]} ('{token[1]}')"
            )
        logger.debug(f"Expected token: {token}")
        return token


# -------------------------------
# Type Checker Implementation
# -------------------------------
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


# -------------------------------
# Main Compiler Flow
# -------------------------------
if __name__ == "__main__":
    logger.info("Starting main compiler flow...")
    if len(sys.argv) < 2:
        print("Usage: python aegis_compiler.py <source_file.ae>")
        sys.exit(1)
    with open(sys.argv[1], "r") as src:
        source_code = src.read()
    # Lex
    tokens = lex(source_code)
    # Parse
    parser = AegisParser(tokens)
    ast = parser.parse()
    # Type Chec
    type_checker = TypeChecker(ast)
    print(type_checker.check())
    # Generate LLVM IR
    code_gen = CodeGenerator(ast)
    llvm_ir = code_gen.generate()
    print("LLVM IR Generated:\n", llvm_ir)
    # JIT Compile & Execute
    jit_compiler = JITCompiler(llvm_ir)
    print(jit_compiler.compile_and_execute())
