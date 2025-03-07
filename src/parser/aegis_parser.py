from antlr4 import InputStream, CommonTokenStream, DiagnosticErrorListener
import sys
import os
from typing import Any, Dict, List, Optional, Union

# Add the generated parser directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'generated'))

# Add the src directory to the path
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.dirname(current_dir)
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

# Import the generated ANTLR classes
from AegisLangLexer import AegisLangLexer
from AegisLangParser import AegisLangParser
from AegisLangListener import AegisLangListener

# Import from our own modules
from lexer.indentation_lexer import AegisIndentationLexer


class AegisErrorListener(DiagnosticErrorListener):
    """
    Custom error listener that provides AI-friendly error messages
    with suggestions for fixing common issues.
    """
    
    def __init__(self):
        super().__init__()
        self.errors = []
        
    def syntaxError(self, recognizer, offendingSymbol, line, column, msg, e):
        # Call the parent method to get diagnostic messages
        super().syntaxError(recognizer, offendingSymbol, line, column, msg, e)
        
        # Create AI-friendly error messages
        if offendingSymbol:
            error_pos = f"line {line}:{column}"
            error_token = offendingSymbol.text if hasattr(offendingSymbol, 'text') else str(offendingSymbol)
            
            # Get expected tokens for better suggestions
            expected_str = "valid token"
            if recognizer:
                expected_tokens = []
                try:
                    expected_tokens_bitset = recognizer.getExpectedTokens()
                    if expected_tokens_bitset:
                        # Try to extract token names differently depending on ANTLR version
                        if hasattr(expected_tokens_bitset, 'toList'):
                            for token_id in expected_tokens_bitset.toList():
                                if token_id < len(recognizer.literalNames):
                                    token_name = recognizer.literalNames[token_id]
                                    if token_name:
                                        expected_tokens.append(token_name)
                        else:
                            # Older ANTLR might not have toList but direct iteration
                            for token_id in expected_tokens_bitset:
                                if token_id < len(recognizer.literalNames):
                                    token_name = recognizer.literalNames[token_id]
                                    if token_name:
                                        expected_tokens.append(token_name)
                except Exception:
                    # If we can't get expected tokens, just use the original message
                    pass
                    
                if expected_tokens:
                    expected_str = ", ".join(expected_tokens)
                
            # Create the error message with suggestion
            error_msg = f"Syntax error at {error_pos}: Unexpected '{error_token}', expected {expected_str}"
            
            # Add helpful suggestions based on common error patterns
            suggestion = self._get_suggestion(error_token, expected_tokens if 'expected_tokens' in locals() else [], line, column)
            if suggestion:
                error_msg += f"\nSuggestion: {suggestion}"
            
            self.errors.append(error_msg)
        else:
            self.errors.append(f"Syntax error at line {line}:{column}: {msg}")
    
    def _get_suggestion(self, offending_token, expected_tokens, line, column):
        """Generate helpful AI-friendly suggestions based on common errors."""
        if 'INDENT' in expected_tokens:
            return "Add an indentation (4 spaces) at the beginning of this line. In Aegis, code blocks must be indented consistently."
        
        if 'DEDENT' in expected_tokens:
            return "Reduce the indentation level for this line to match its parent block."
        
        if 'COLON' in expected_tokens:
            return "Add a colon ':' after this declaration to start a new block."
        
        if offending_token == 'DEDENT' and 'IDENTIFIER' in expected_tokens:
            return "This line is not properly indented. Make sure all lines in the same block have the same indentation level."
            
        # More specific suggestions could be added here
        
        return None


class AegisParser:
    """
    Main parser for the Aegis programming language.
    Uses ANTLR4-generated parser and a custom indentation-aware lexer.
    """
    
    def __init__(self):
        self.ast = None
        self.errors = []
    
    def parse(self, input_text: str, filename: str = "<input>") -> Dict[str, Any]:
        """
        Parse the input text and return an AST representation.
        
        Args:
            input_text: The source code to parse
            filename: Source file name for error reporting
            
        Returns:
            An abstract syntax tree representation as a dictionary
        """
        # Preprocess indentation
        indentation_lexer = AegisIndentationLexer(None)  # We don't need the actual lexer for preprocessing
        preprocessed_text = indentation_lexer.process_indentation(input_text)
        
        # Add indentation errors if any
        self.errors.extend([error["message"] + "\n" + error["suggestion"] 
                           for error in indentation_lexer.indent_errors])
        
        # Create the input stream
        input_stream = InputStream(preprocessed_text)
        
        # Set up the lexer and parser
        lexer = AegisLangLexer(input_stream)
        lexer.removeErrorListeners()
        
        # Create token stream and parser
        tokens = CommonTokenStream(lexer)
        parser = AegisLangParser(tokens)
        
        # Set up error handling
        error_listener = AegisErrorListener()
        parser.removeErrorListeners()
        parser.addErrorListener(error_listener)
        
        # Attempt to parse the input
        try:
            # Parse the input text
            parse_tree = parser.program()
            
            # Store any errors that occurred during parsing
            self.errors.extend(error_listener.errors)
            
            # If there were errors, return error information
            if self.errors:
                return {
                    "type": "Program",
                    "modules": [],
                    "errors": self.errors
                }
            
            # Convert to our own AST format
            visitor = AegisASTVisitor()
            self.ast = visitor.visit(parse_tree)
            
            return self.ast
            
        except Exception as e:
            # Handle any exceptions that occurred during parsing
            error_msg = str(e)
            self.errors.append(f"Error parsing {filename}: {error_msg}")
            
            return {
                "type": "Program",
                "modules": [],
                "errors": self.errors
            }
    
    def parse_file(self, filepath: str) -> Dict[str, Any]:
        """
        Parse a file and return an AST representation.
        
        Args:
            filepath: Path to the file to parse
            
        Returns:
            An abstract syntax tree representation as a dictionary
        """
        with open(filepath, 'r') as file:
            input_text = file.read()
        return self.parse(input_text, filepath)


class AegisASTVisitor:
    """
    Visitor class that converts the ANTLR parse tree to a custom AST.
    """
    
    def __init__(self):
        self.symbol_table = {}
        self.current_module = None
        self.current_struct = None
        self.current_function = None
        self.source_positions = {}  # Track source positions for better error messages
    
    def visit(self, ctx):
        """Generic visit method that dispatches to specific methods."""
        if ctx is None:
            return None
            
        # Record source position if available
        if hasattr(ctx, 'start') and ctx.start:
            position = {
                'line': ctx.start.line,
                'column': ctx.start.column,
                'start': ctx.start.start,
                'stop': ctx.stop.stop if ctx.stop else ctx.start.stop
            }
            self.source_positions[id(ctx)] = position
        
        # Dispatch to appropriate visitor method
        method_name = f'visit_{ctx.__class__.__name__.lower()}'
        visitor = getattr(self, method_name, self.visit_fallback)
        result = visitor(ctx)
        
        # Add source position to result if it's a dictionary
        if isinstance(result, dict) and id(ctx) in self.source_positions:
            result['position'] = self.source_positions[id(ctx)]
            
        return result
    
    def visit_fallback(self, ctx):
        """Default fallback if no specific visitor is found."""
        if hasattr(ctx, 'children') and ctx.children:
            results = [self.visit(child) for child in ctx.children if child is not None]
            return results[-1] if results else None
        return None
    
    def visit_program(self, ctx):
        """Visit the root program node."""
        modules = []
        for module_ctx in ctx.moduleDecl():
            module_ast = self.visit_moduledecl(module_ctx)
            if module_ast:
                modules.append(module_ast)
        return {"type": "Program", "modules": modules}
    
    def visit_moduledecl(self, ctx):
        """Visit a module declaration."""
        name = self.visit(ctx.identifier())
        self.current_module = name
        
        # Process module body
        structs = []
        enums = []
        functions = []
        constants = []
        
        # Process each declaration in the module
        # First, look for struct declarations
        if hasattr(ctx, 'structDecl') and ctx.structDecl():
            for struct_ctx in ctx.structDecl():
                struct_ast = self.visit_structdecl(struct_ctx)
                if struct_ast:
                    structs.append(struct_ast)
        
        # Look for enum declarations
        if hasattr(ctx, 'enumDecl') and ctx.enumDecl():
            for enum_ctx in ctx.enumDecl():
                enum_ast = self.visit_enumdecl(enum_ctx)
                if enum_ast:
                    enums.append(enum_ast)
        
        # Look for function declarations
        if hasattr(ctx, 'fnDecl') and ctx.fnDecl():
            for fn_ctx in ctx.fnDecl():
                fn_ast = self.visit_fndecl(fn_ctx)
                if fn_ast:
                    functions.append(fn_ast)
        
        # Look for constant declarations
        if hasattr(ctx, 'constDecl') and ctx.constDecl():
            for const_ctx in ctx.constDecl():
                const_ast = self.visit_constdecl(const_ctx)
                if const_ast:
                    constants.append(const_ast)
        
        self.current_module = None
        
        return {
            "type": "Module",
            "name": name,
            "structs": structs,
            "enums": enums,
            "functions": functions,
            "constants": constants
        }
    
    def visit_structdecl(self, ctx):
        """Visit a struct declaration."""
        name = self.visit(ctx.identifier())
        self.current_struct = name
        fields = []
        
        # Process fields
        if hasattr(ctx, 'fieldDecl') and ctx.fieldDecl():
            for field_ctx in ctx.fieldDecl():
                field_ast = self.visit_fielddecl(field_ctx)
                if field_ast:
                    fields.append(field_ast)
        
        self.current_struct = None
        
        return {
            "type": "Struct",
            "name": name,
            "fields": fields
        }
    
    def visit_fielddecl(self, ctx):
        """Visit a field declaration in a struct."""
        name = self.visit(ctx.identifier())
        field_type = self.visit(ctx.type_())
        
        # Check for default value
        default_value = None
        if hasattr(ctx, 'expression') and ctx.expression():
            default_value = self.visit(ctx.expression())
        
        return {
            "type": "Field",
            "name": name,
            "field_type": field_type,
            "default_value": default_value
        }
    
    def visit_enumdecl(self, ctx):
        """Visit an enum declaration."""
        name = self.visit(ctx.identifier())
        variants = []
        
        # Process variants
        if hasattr(ctx, 'enumVariant') and ctx.enumVariant():
            for variant_ctx in ctx.enumVariant():
                variant_ast = self.visit_enumvariant(variant_ctx)
                if variant_ast:
                    variants.append(variant_ast)
        
        return {
            "type": "Enum",
            "name": name,
            "variants": variants
        }
    
    def visit_enumvariant(self, ctx):
        """Visit an enum variant."""
        name = self.visit(ctx.identifier())
        associated_types = []
        
        # Process associated types
        if hasattr(ctx, 'type_') and ctx.type_():
            for type_ctx in ctx.type_():
                type_ast = self.visit(type_ctx)
                if type_ast:
                    associated_types.append(type_ast)
        
        return {
            "type": "EnumVariant",
            "name": name,
            "associated_types": associated_types
        }
    
    def visit_fndecl(self, ctx):
        """Visit a function declaration."""
        name = self.visit(ctx.identifier())
        self.current_function = name
        
        # Process parameters
        parameters = []
        if hasattr(ctx, 'paramList') and ctx.paramList():
            for param_ctx in ctx.paramList().parameter():
                param_ast = self.visit_parameter(param_ctx)
                if param_ast:
                    parameters.append(param_ast)
        
        # Process return type
        return_type = None
        if hasattr(ctx, 'type_') and ctx.type_():
            return_type = self.visit(ctx.type_())
        
        # Process function body
        body = []
        if hasattr(ctx, 'statement') and ctx.statement():
            for stmt_ctx in ctx.statement():
                stmt_ast = self.visit(stmt_ctx)
                if stmt_ast:
                    body.append(stmt_ast)
        
        self.current_function = None
        
        return {
            "type": "Function",
            "name": name,
            "parameters": parameters,
            "return_type": return_type,
            "body": body
        }
    
    def visit_parameter(self, ctx):
        """Visit a function parameter."""
        name = self.visit(ctx.identifier())
        param_type = self.visit(ctx.type_())
        
        return {
            "type": "Parameter",
            "name": name,
            "parameter_type": param_type
        }
    
    def visit_identifier(self, ctx):
        """Visit an identifier and return its name."""
        return ctx.getText()
    
    # Type visitor methods
    def visit_primitivetype(self, ctx):
        """Visit a primitive type node."""
        return ctx.PRIMITIVE_TYPE().getText()
    
    def visit_userdefinedtype(self, ctx):
        """Visit a user-defined type node."""
        return self.visit(ctx.identifier())
    
    def visit_optiontype(self, ctx):
        """Visit an Option<T> type node."""
        inner_type = self.visit(ctx.type_())
        return {
            "type": "optionType",
            "inner_type": inner_type
        }
    
    def visit_resulttype(self, ctx):
        """Visit a Result<T, E> type node."""
        value_type = self.visit(ctx.type_(0))
        error_type = self.visit(ctx.type_(1))
        return {
            "type": "resultType",
            "value_type": value_type,
            "error_type": error_type
        }
    
    def visit_arraytype(self, ctx):
        """Visit an array type node."""
        element_type = self.visit(ctx.type_())
        return {
            "type": "arrayType",
            "element_type": element_type
        }
    
    # Statement visitor methods
    def visit_variabledecl(self, ctx):
        """Visit a variable declaration."""
        name = self.visit(ctx.identifier())
        var_type = self.visit(ctx.type_())
        
        # Check for initialization
        init_value = None
        if hasattr(ctx, 'expression') and ctx.expression():
            init_value = self.visit(ctx.expression())
        
        return {
            "type": "VariableDeclaration",
            "name": name,
            "var_type": var_type,
            "init_value": init_value
        }
    
    def visit_returnstmt(self, ctx):
        """Visit a return statement."""
        value = None
        if hasattr(ctx, 'expression') and ctx.expression():
            value = self.visit(ctx.expression())
        
        return {
            "type": "ReturnStatement",
            "value": value
        }
    
    # Additional visitor methods would be implemented as needed
    
    def visit_constructororfunctionexpr(self, ctx):
        """Visit a constructor or function call expression."""
        name = self.visit(ctx.identifier())
        
        # Process arguments
        arguments = []
        if hasattr(ctx, 'expressionList') and ctx.expressionList():
            # Handle argument expressions
            for expr in ctx.expressionList().expression():
                arg = self.visit(expr)
                if arg:
                    arguments.append(arg)
        
        return {
            "type": "ConstructorOrFunctionCall",
            "name": name,
            "arguments": arguments
        }
    
    def visit_methodcallexpr(self, ctx):
        """Visit a method call expression."""
        target = self.visit(ctx.expression())
        
        # Process arguments
        arguments = []
        if hasattr(ctx, 'expressionList') and ctx.expressionList():
            # Handle argument expressions
            for expr in ctx.expressionList().expression():
                arg = self.visit(expr)
                if arg:
                    arguments.append(arg)
        
        return {
            "type": "MethodCall",
            "target": target,
            "arguments": arguments
        }
    
    def visit_expressionstmt(self, ctx):
        """Visit an expression statement."""
        return {
            "type": "ExpressionStatement",
            "expression": self.visit(ctx.expression())
        }


def test_parser():
    """Test function to verify the parser works."""
    parser = AegisParser()
    test_code = """
module UserSystem:
    struct User:
        name: string
        age: int
    
    fn get_user(name: string) -> User:
        return User(name, 25)
    """
    
    try:
        ast = parser.parse(test_code)
        print("Parsing successful!")
        print(ast)
        return True
    except Exception as e:
        print(f"Parsing error: {e}")
        return False


if __name__ == "__main__":
    test_parser() 