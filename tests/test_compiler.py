# tests/test_compiler.py

"""
Test suite for AegisLang Compiler.
Uses unittest to ensure the compiler (lexer, parser, type checker, IR generator) works.
"""

import unittest
from compiler.aegis_compiler import lex, AegisParser, TypeChecker, CodeGenerator

class TestAegisCompiler(unittest.TestCase):
    def setUp(self):
        # Example AegisLang source to test
        self.source_code = """
module TestModule:
    struct Test:
        id: int
        name: string

    fn get_test(id: int) -> Test:
        return Test(id, "Sample")
"""
        self.tokens = lex(self.source_code)
        self.parser = AegisParser(self.tokens)
        self.ast = self.parser.parse()

    def test_type_checker(self):
        type_checker = TypeChecker(self.ast)
        result = type_checker.check()
        self.assertEqual(result, "Semantic Analysis Passed")

    def test_code_generation(self):
        code_gen = CodeGenerator(self.ast)
        llvm_ir = code_gen.generate()
        self.assertIn("define", llvm_ir)

if __name__ == '__main__':
    unittest.main()
