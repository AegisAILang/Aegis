import unittest
from compiler.aegis_compiler import lex, AegisParser, TypeChecker, CodeGenerator


class CompilerTest(unittest.TestCase):
    def setUp(self):
        self.source_code = """
        module TestModule:
            struct User:
                name: string
                age: int

            fn create_user(name: string) -> User:
                return User(name, 25)
        """

    def test_lexer(self):
        tokens = lex(self.source_code)
        self.assertTrue(len(tokens) > 0)

    def test_parser(self):
        tokens = lex(self.source_code)
        parser = AegisParser(tokens)
        ast = parser.parse()
        self.assertEqual(ast.node_type, "Module")

    def test_type_checker(self):
        tokens = lex(self.source_code)
        parser = AegisParser(tokens)
        ast = parser.parse()
        type_checker = TypeChecker(ast)
        self.assertEqual(type_checker.check(), "Semantic Analysis Passed")


if __name__ == "__main__":
    unittest.main()
