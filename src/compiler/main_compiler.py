"""
AegisLang Compiler
This file implements the Lexer, Parser, Type Checker, LLVM IR Generator, and JIT Compiler.

The compiler follows a standard pipeline:
lex → parse → type-check → generate IR → JIT execute

The semantic analysis phase ensures type safety and validity before code generation occurs.
"""

import sys
import os
from src.lexer.lexer import lex
from src.parser.parser import AegisParser
from src.semantic.type_checker import TypeChecker
from src.semantic.symbol_table import SymbolTable 
from src.compiler.code_generator import CodeGenerator
from src.jit.jit_compiler import JITCompiler
from utils.logger import get_logger

logger = get_logger(__name__)

# -------------------------------
# Main Compiler Flow
# -------------------------------
def compile_file(source_path):
    """
    Compile an Aegis source file (.ae) through the full compilation pipeline.
    
    Args:
        source_path: Path to the source file
        
    Returns:
        A tuple of (success, result) where:
        - success is a boolean indicating if compilation succeeded
        - result contains either the execution result or error messages
    """
    try:
        # Read source code
        logger.info(f"Reading source file: {source_path}")
        with open(source_path, "r") as f:
            source_code = f.read()
            
        # Extract file name for error reporting
        file_name = os.path.basename(source_path)
        
        # 1. Lexical Analysis
        logger.info("Starting lexical analysis")
        tokens = lex(source_code)
        logger.info(f"Lexical analysis complete: {len(tokens)} tokens")
        
        # 2. Parsing
        logger.info("Starting parsing")
        parser = AegisParser(tokens)
        ast = parser.parse()
        
        if parser.errors:
            # Parse errors found, display and return
            logger.error(f"Parsing failed with {len(parser.errors)} errors")
            error_messages = []
            for error in parser.errors:
                error_messages.append(f"{file_name}:{error.line}:{error.column}: Parse Error: {error.message}")
                # Add suggestion if available
                if hasattr(error, 'suggestion') and error.suggestion:
                    error_messages.append(f"Suggestion: {error.suggestion}")
            
            return False, "\n".join(error_messages)
        
        logger.info("Parsing complete")
        
        # 3. Semantic Analysis
        logger.info("Starting semantic analysis")
        symbol_table = SymbolTable()  # Create new symbol table
        type_checker = TypeChecker()  # Create type checker
        semantic_errors = type_checker.check(ast)  # Perform semantic analysis
        
        if semantic_errors:
            # Semantic errors found, display and return
            logger.error(f"Semantic analysis failed with {len(semantic_errors)} errors")
            error_messages = []
            for error in semantic_errors:
                error_messages.append(f"{error}")  # TypeCheckError already formats properly
            
            return False, "\n".join(error_messages)
            
        logger.info("Semantic analysis complete - no errors found")
        
        # 4. Code Generation (only if no semantic errors)
        logger.info("Starting LLVM IR generation")
        code_gen = CodeGenerator(ast)
        llvm_ir = code_gen.generate()
        logger.info("LLVM IR generation complete")
        
        # 5. JIT Compilation and Execution
        logger.info("Starting JIT compilation and execution")
        jit_compiler = JITCompiler(llvm_ir)
        execution_result = jit_compiler.compile_and_execute()
        logger.info("Execution complete")
        
        return True, execution_result
        
    except Exception as e:
        logger.error(f"Compilation failed with exception: {str(e)}")
        return False, f"Internal compiler error: {str(e)}"

def display_error(error_message):
    """Format and display an error message with AI-friendly suggestions."""
    print("❌ Compilation Error:")
    print(error_message)

def main():
    """Main entry point for the compiler."""
    logger.info("Starting Aegis compiler")
    
    if len(sys.argv) < 2:
        print("Usage: python aegis_compiler.py <source_file.ae>")
        return 1
        
    source_path = sys.argv[1]
    
    # Check if file exists
    if not os.path.exists(source_path):
        print(f"Error: File not found: {source_path}")
        return 1
        
    # Check file extension
    if not source_path.endswith('.ae'):
        print(f"Warning: File does not have .ae extension: {source_path}")
    
    # Compile the file
    success, result = compile_file(source_path)
    
    if not success:
        display_error(result)
        return 1
    else:
        print("✅ Compilation and execution successful:")
        print(result)
        return 0

if __name__ == "__main__":
    sys.exit(main())
