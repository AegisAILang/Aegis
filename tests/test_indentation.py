"""
Test suite for the AegisIndentationLexer.

Tests the indentation handling capabilities of the lexer, ensuring proper
INDENT and DEDENT tokens are created and error detection works as expected.
"""

import unittest
from src.lexer.indentation_lexer import AegisIndentationLexer
from antlr4 import InputStream, CommonTokenStream
from AegisLangLexer import AegisLangLexer  # Auto-generated from ANTLR4

class MockLexer:
    """Mock lexer for testing the indentation lexer"""
    def __init__(self):
        self.tokens = []

class TestIndentationLexer(unittest.TestCase):
    def setUp(self):
        self.lexer = AegisIndentationLexer(MockLexer())

    def test_basic_indentation(self):
        """Test basic indentation patterns"""
        source = """
module Test:
    fn function():
        statement1
        statement2
    fn function2():
        statement3
"""
        processed = self.lexer.process_indentation(source)
        self.assertIn("INDENT", processed)
        self.assertIn("DEDENT", processed)

    def test_multi_level_indentation(self):
        """Test multiple levels of indentation"""
        source = """
module Test:
    fn function():
        if condition:
            statement1
            statement2
        statement3
"""
        processed = self.lexer.process_indentation(source)
        lines = processed.split('\n')
        indent_count = sum(1 for line in lines if "INDENT" in line)
        dedent_count = sum(1 for line in lines if "DEDENT" in line)
        
        # Should have 2 indents (for fn and if) and 2 dedents
        self.assertEqual(indent_count, 2)
        self.assertEqual(dedent_count, 2)

    def test_mixed_indentation_error(self):
        """Test error detection with mixed indentation"""
        source = """
module Test:
    fn function():
        statement1
       wrong_indent
"""
        self.lexer.process_indentation(source)
        # Should detect the indentation error
        self.assertTrue(len(self.lexer.indent_errors) > 0)
        error = self.lexer.indent_errors[0]
        self.assertIn("IndentationError", error["type"])
        self.assertIn("wrong_indent", source)

    def test_over_indentation_error(self):
        """Test error detection with over-indentation"""
        source = """
module Test:
    fn function():
        statement1
            over_indented
"""
        processed = self.lexer.process_indentation(source)
        # Should still process it with INDENT but record an error
        self.assertIn("INDENT", processed)
        self.assertTrue(len(self.lexer.indent_errors) > 0)

    def test_empty_lines_and_comments(self):
        """Test handling of empty lines and comments"""
        source = """
module Test:
    # This is a comment
    
    fn function():
        statement1
        # Another comment
        
        statement2
"""
        processed = self.lexer.process_indentation(source)
        # Comments and empty lines should be preserved
        self.assertIn("# This is a comment", processed)
        self.assertIn("# Another comment", processed)
        
        # Proper indentation should still work
        self.assertIn("INDENT", processed)

    def test_dedent_handling(self):
        """Test multiple dedent levels are handled correctly"""
        source = """
module Test:
    fn outer():
        if condition:
            statement1
        statement2
"""
        processed = self.lexer.process_indentation(source)
        # Check that we dedent properly from the if block
        dedent_line = None
        for line in processed.split('\n'):
            if "statement2" in line and "DEDENT" in line:
                dedent_line = line
                break
        
        self.assertIsNotNone(dedent_line)
        self.assertIn("DEDENT", dedent_line)

    def test_complex_nesting(self):
        """Test complex nesting patterns"""
        source = """
module Test:
    struct User:
        name: string
        age: int
        
    fn get_user(id: int) -> Option<User>:
        if id > 0:
            if db_connected():
                return Some(User("Test", 25))
            else:
                return None
        return None
"""
        processed = self.lexer.process_indentation(source)
        
        # Count indents and dedents
        indent_count = sum(1 for line in processed.split('\n') if "INDENT" in line)
        dedent_count = sum(1 for line in processed.split('\n') if "DEDENT" in line)
        
        # Should have appropriate number of indents and dedents
        self.assertEqual(indent_count, 3)  # module->struct, module->fn, fn->if, if->if
        self.assertEqual(dedent_count, 3)  # or more with final dedents

    def test_option_type_dsl_pattern(self):
        """Test indentation with Option<T> and DSL-like patterns"""
        source = """
module OptTest:
    fn process_optional(opt: Option<int>) -> int:
        match opt:
            Some(value) => 
                if value > 10:
                    return value * 2
                else:
                    return value
            None => 
                return 0
"""
        processed = self.lexer.process_indentation(source)
        
        # Should handle the match statement and nested if-else properly
        self.assertIn("INDENT", processed)
        self.assertIn("DEDENT", processed)
        
        # No indentation errors
        self.assertEqual(len(self.lexer.indent_errors), 0)

if __name__ == "__main__":
    unittest.main()