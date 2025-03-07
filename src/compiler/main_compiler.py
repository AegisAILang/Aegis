"""
AegisLang Compiler
This file implements the Lexer, Parser, Type Checker, LLVM IR Generator, and JIT Compiler.
"""

## lex → parse → type-check → generate IR → JIT execute.

import sys
from src.lexer.lexer import lex
from src.parser.parser import AegisParser
from src.compiler.type_checker import TypeChecker
from src.compiler.code_generator import CodeGenerator
from src.jit.jit_compiler import JITCompiler
from utils.logger import get_logger

logger = get_logger(__name__)
# -------------------------------
# Main Compiler Flow
# -------------------------------
def compile_file(source_path):
    with open(source_path, "r") as f:
        code = f.read()

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

if __name__ == "__main__":
    logger.info("Starting main compiler flow...")
    if len(sys.argv) < 2:
        print("Usage: python aegis_compiler.py <source_file.ae>")
        sys.exit(1)
    with open(sys.argv[1], "r") as src:
        source_code = src.read()
    compile_file(source_code)
