"""
Test suite for the semantic analysis components of Aegis.

Tests type checking, symbol resolution, and semantic validation to ensure
the language adheres to its type safety and deterministic design principles.
"""

import unittest
from src.semantic.type_checker import TypeChecker
from src.semantic.symbol_table import SymbolTable, Symbol, SymbolType, Scope
from src.parser.aeigix_ast_visitor import SourcePosition

class TestSemanticAnalysis(unittest.TestCase):
    def setUp(self):
        self.type_checker = TypeChecker()
        
    def test_basic_type_checking(self):
        """Test basic type checking for compatible types"""
        # Create a simple AST with an assignment of compatible types
        ast = {
            "node_type": "module",
            "name": "Test",
            "children": [{
                "node_type": "variable_declaration",
                "name": "x",
                "var_type": {"name": "int"},
                "init_value": {
                    "node_type": "literal",
                    "literal_type": "int",
                    "value": 42,
                    "position": SourcePosition(1, 1, "test.ae")
                },
                "position": SourcePosition(1, 1, "test.ae")
            }],
            "position": SourcePosition(1, 1, "test.ae")
        }
        
        errors = self.type_checker.check(ast)
        self.assertEqual(len(errors), 0, "No type errors should be found")
        
    def test_incompatible_types(self):
        """Test detection of incompatible types"""
        # Create an AST with an incompatible type assignment
        ast = {
            "node_type": "module",
            "name": "Test",
            "children": [{
                "node_type": "variable_declaration",
                "name": "x",
                "var_type": {"name": "int"},
                "init_value": {
                    "node_type": "literal",
                    "literal_type": "string",
                    "value": "hello",
                    "position": SourcePosition(1, 1, "test.ae")
                },
                "position": SourcePosition(1, 1, "test.ae")
            }],
            "position": SourcePosition(1, 1, "test.ae")
        }
        
        errors = self.type_checker.check(ast)
        self.assertGreater(len(errors), 0, "Type error should be detected")
        self.assertIn("type", str(errors[0]).lower())

    def test_undefined_symbol(self):
        """Test detection of undefined symbols"""
        # Create an AST with an undefined variable reference
        ast = {
            "node_type": "module",
            "name": "Test",
            "children": [{
                "node_type": "function",
                "name": "test_func",
                "parameters": [],
                "return_type": {"name": "void"},
                "body": [{
                    "node_type": "expression_statement",
                    "expression": {
                        "node_type": "identifier",
                        "name": "undefined_var",
                        "position": SourcePosition(2, 5, "test.ae")
                    },
                    "position": SourcePosition(2, 5, "test.ae")
                }],
                "position": SourcePosition(1, 1, "test.ae")
            }],
            "position": SourcePosition(1, 1, "test.ae")
        }
        
        errors = self.type_checker.check(ast)
        self.assertGreater(len(errors), 0, "Undefined symbol error should be detected")
        self.assertIn("undefined", str(errors[0]).lower())

    def test_missing_return(self):
        """Test detection of missing return in non-void functions"""
        # Create a function with a non-void return type but no return statement
        ast = {
            "node_type": "module",
            "name": "Test",
            "children": [{
                "node_type": "function",
                "name": "no_return",
                "parameters": [],
                "return_type": {"name": "int"},
                "body": [{
                    "node_type": "variable_declaration",
                    "name": "x",
                    "var_type": {"name": "int"},
                    "init_value": {
                        "node_type": "literal",
                        "literal_type": "int",
                        "value": 42,
                        "position": SourcePosition(2, 5, "test.ae")
                    },
                    "position": SourcePosition(2, 5, "test.ae")
                }],
                "position": SourcePosition(1, 1, "test.ae")
            }],
            "position": SourcePosition(1, 1, "test.ae")
        }
        
        errors = self.type_checker.check(ast)
        self.assertGreater(len(errors), 0, "Missing return error should be detected")
        self.assertIn("return", str(errors[0]).lower())

    def test_option_type(self):
        """Test type checking with Option<T> types"""
        # Create a function that returns an Option<int>
        ast = {
            "node_type": "module",
            "name": "Test",
            "children": [{
                "node_type": "function",
                "name": "get_optional",
                "parameters": [],
                "return_type": {
                    "name": "Option",
                    "type_params": [{"name": "int"}],
                    "position": SourcePosition(1, 20, "test.ae")
                },
                "body": [{
                    "node_type": "return_statement",
                    "value": {
                        "node_type": "constructor_call",
                        "name": "Some",
                        "arguments": [{
                            "node_type": "literal",
                            "literal_type": "int",
                            "value": 42,
                            "position": SourcePosition(2, 15, "test.ae")
                        }],
                        "position": SourcePosition(2, 12, "test.ae")
                    },
                    "position": SourcePosition(2, 5, "test.ae")
                }],
                "position": SourcePosition(1, 1, "test.ae")
            }],
            "position": SourcePosition(1, 1, "test.ae")
        }
        
        errors = self.type_checker.check(ast)
        self.assertEqual(len(errors), 0, "Option<T> should be correctly type checked")

    def test_match_exhaustiveness(self):
        """Test that match expressions are checked for exhaustiveness"""
        # Create a match expression on an Option<T> type
        ast = {
            "node_type": "module",
            "name": "Test",
            "children": [{
                "node_type": "function",
                "name": "handle_option",
                "parameters": [{
                    "name": "opt",
                    "param_type": {
                        "name": "Option",
                        "type_params": [{"name": "int"}],
                        "position": SourcePosition(1, 25, "test.ae")
                    },
                    "position": SourcePosition(1, 20, "test.ae")
                }],
                "return_type": {"name": "int"},
                "body": [{
                    "node_type": "match_statement",
                    "subject": {
                        "node_type": "identifier",
                        "name": "opt",
                        "position": SourcePosition(2, 11, "test.ae")
                    },
                    "branches": [
                        {
                            "pattern": {
                                "node_type": "constructor_pattern",
                                "name": "Some",
                                "bindings": [{
                                    "node_type": "binding_pattern",
                                    "name": "value",
                                    "position": SourcePosition(3, 15, "test.ae")
                                }],
                                "position": SourcePosition(3, 5, "test.ae")
                            },
                            "body": {
                                "node_type": "return_statement",
                                "value": {
                                    "node_type": "identifier",
                                    "name": "value",
                                    "position": SourcePosition(3, 25, "test.ae")
                                },
                                "position": SourcePosition(3, 18, "test.ae")
                            },
                            "guard": None
                        }
                        # Missing None case
                    ],
                    "position": SourcePosition(2, 5, "test.ae")
                }],
                "position": SourcePosition(1, 1, "test.ae")
            }],
            "position": SourcePosition(1, 1, "test.ae")
        }
        
        errors = self.type_checker.check(ast)
        self.assertGreater(len(errors), 0, "Non-exhaustive match should be detected")
        self.assertIn("exhaustive", str(errors[0]).lower())

    def test_concurrent_task_types(self):
        """Test type checking with async/await and Task<T> types"""
        # Create an async function returning a Task<string>
        ast = {
            "node_type": "module",
            "name": "Test",
            "children": [{
                "node_type": "function",
                "name": "fetch_data",
                "parameters": [],
                "return_type": {
                    "name": "Task",
                    "type_params": [{"name": "string"}],
                    "position": SourcePosition(1, 20, "test.ae")
                },
                "is_async": True,
                "body": [{
                    "node_type": "return_statement",
                    "value": {
                        "node_type": "literal",
                        "literal_type": "string",
                        "value": "data",
                        "position": SourcePosition(2, 12, "test.ae")
                    },
                    "position": SourcePosition(2, 5, "test.ae")
                }],
                "position": SourcePosition(1, 1, "test.ae")
            }, {
                # Another function that awaits the first function
                "node_type": "function",
                "name": "process_data",
                "parameters": [],
                "return_type": {"name": "string"},
                "body": [{
                    "node_type": "variable_declaration",
                    "name": "data",
                    "var_type": {"name": "string"},
                    "init_value": {
                        "node_type": "await_expression",
                        "expression": {
                            "node_type": "function_call",
                            "name": "fetch_data",
                            "arguments": [],
                            "position": SourcePosition(2, 17, "test.ae")
                        },
                        "position": SourcePosition(2, 11, "test.ae")
                    },
                    "position": SourcePosition(2, 5, "test.ae")
                }, {
                    "node_type": "return_statement",
                    "value": {
                        "node_type": "identifier",
                        "name": "data",
                        "position": SourcePosition(3, 12, "test.ae")
                    },
                    "position": SourcePosition(3, 5, "test.ae")
                }],
                "position": SourcePosition(1, 1, "test.ae")
            }],
            "position": SourcePosition(1, 1, "test.ae")
        }
        
        errors = self.type_checker.check(ast)
        self.assertEqual(len(errors), 0, "Concurrent types should be correctly checked")

    def test_result_type(self):
        """Test type checking with Result<T, E> types"""
        # Create a function returning Result<int, string>
        ast = {
            "node_type": "module",
            "name": "Test",
            "children": [{
                "node_type": "function",
                "name": "divide",
                "parameters": [
                    {
                        "name": "a",
                        "param_type": {"name": "int"},
                        "position": SourcePosition(1, 15, "test.ae")
                    },
                    {
                        "name": "b",
                        "param_type": {"name": "int"},
                        "position": SourcePosition(1, 25, "test.ae")
                    }
                ],
                "return_type": {
                    "name": "Result",
                    "type_params": [{"name": "int"}, {"name": "string"}],
                    "position": SourcePosition(1, 35, "test.ae")
                },
                "body": [{
                    "node_type": "if_statement",
                    "condition": {
                        "node_type": "binary_operation",
                        "operator": "==",
                        "left": {
                            "node_type": "identifier",
                            "name": "b",
                            "position": SourcePosition(2, 9, "test.ae")
                        },
                        "right": {
                            "node_type": "literal",
                            "literal_type": "int",
                            "value": 0,
                            "position": SourcePosition(2, 14, "test.ae")
                        },
                        "position": SourcePosition(2, 11, "test.ae")
                    },
                    "then_branch": [{
                        "node_type": "return_statement",
                        "value": {
                            "node_type": "constructor_call",
                            "name": "Err",
                            "arguments": [{
                                "node_type": "literal",
                                "literal_type": "string",
                                "value": "Division by zero",
                                "position": SourcePosition(3, 20, "test.ae")
                            }],
                            "position": SourcePosition(3, 16, "test.ae")
                        },
                        "position": SourcePosition(3, 9, "test.ae")
                    }],
                    "else_branch": [{
                        "node_type": "return_statement",
                        "value": {
                            "node_type": "constructor_call",
                            "name": "Ok",
                            "arguments": [{
                                "node_type": "binary_operation",
                                "operator": "/",
                                "left": {
                                    "node_type": "identifier",
                                    "name": "a",
                                    "position": SourcePosition(5, 19, "test.ae")
                                },
                                "right": {
                                    "node_type": "identifier",
                                    "name": "b",
                                    "position": SourcePosition(5, 23, "test.ae")
                                },
                                "position": SourcePosition(5, 21, "test.ae")
                            }],
                            "position": SourcePosition(5, 16, "test.ae")
                        },
                        "position": SourcePosition(5, 9, "test.ae")
                    }],
                    "position": SourcePosition(2, 5, "test.ae")
                }],
                "position": SourcePosition(1, 1, "test.ae")
            }],
            "position": SourcePosition(1, 1, "test.ae")
        }
        
        errors = self.type_checker.check(ast)
        self.assertEqual(len(errors), 0, "Result<T, E> should be correctly type checked")

    def test_dsl_pattern(self):
        """Test type checking with DSL-like patterns"""
        # Create a DSL-like pattern for a query builder
        ast = {
            "node_type": "module",
            "name": "QueryDSL",
            "children": [{
                "node_type": "struct",
                "name": "Query",
                "fields": [
                    {
                        "node_type": "field",
                        "name": "table",
                        "field_type": {"name": "string"},
                        "position": SourcePosition(2, 5, "test.ae")
                    },
                    {
                        "node_type": "field",
                        "name": "conditions",
                        "field_type": {"name": "string"},
                        "position": SourcePosition(3, 5, "test.ae")
                    }
                ],
                "methods": [{
                    "node_type": "function",
                    "name": "where",
                    "parameters": [
                        {
                            "name": "self",
                            "param_type": {"name": "Query"},
                            "position": SourcePosition(5, 15, "test.ae")
                        },
                        {
                            "name": "condition",
                            "param_type": {"name": "string"},
                            "position": SourcePosition(5, 25, "test.ae")
                        }
                    ],
                    "return_type": {"name": "Query"},
                    "body": [{
                        "node_type": "return_statement",
                        "value": {
                            "node_type": "constructor_call",
                            "name": "Query",
                            "arguments": [
                                {
                                    "node_type": "member_access",
                                    "object": {
                                        "node_type": "identifier",
                                        "name": "self",
                                        "position": SourcePosition(6, 16, "test.ae")
                                    },
                                    "member": "table",
                                    "position": SourcePosition(6, 21, "test.ae")
                                },
                                {
                                    "node_type": "binary_operation",
                                    "operator": "+",
                                    "left": {
                                        "node_type": "member_access",
                                        "object": {
                                            "node_type": "identifier",
                                            "name": "self",
                                            "position": SourcePosition(6, 28, "test.ae")
                                        },
                                        "member": "conditions",
                                        "position": SourcePosition(6, 33, "test.ae")
                                    },
                                    "right": {
                                        "node_type": "identifier",
                                        "name": "condition",
                                        "position": SourcePosition(6, 50, "test.ae")
                                    },
                                    "position": SourcePosition(6, 48, "test.ae")
                                }
                            ],
                            "position": SourcePosition(6, 16, "test.ae")
                        },
                        "position": SourcePosition(6, 9, "test.ae")
                    }],
                    "position": SourcePosition(5, 5, "test.ae")
                }],
                "position": SourcePosition(1, 1, "test.ae")
            }, {
                "node_type": "function",
                "name": "from",
                "parameters": [{
                    "name": "table",
                    "param_type": {"name": "string"},
                    "position": SourcePosition(10, 15, "test.ae")
                }],
                "return_type": {"name": "Query"},
                "body": [{
                    "node_type": "return_statement",
                    "value": {
                        "node_type": "constructor_call",
                        "name": "Query",
                        "arguments": [
                            {
                                "node_type": "identifier",
                                "name": "table",
                                "position": SourcePosition(11, 16, "test.ae")
                            },
                            {
                                "node_type": "literal",
                                "literal_type": "string",
                                "value": "",
                                "position": SourcePosition(11, 23, "test.ae")
                            }
                        ],
                        "position": SourcePosition(11, 12, "test.ae")
                    },
                    "position": SourcePosition(11, 5, "test.ae")
                }],
                "position": SourcePosition(10, 1, "test.ae")
            }],
            "position": SourcePosition(1, 1, "test.ae")
        }
        
        errors = self.type_checker.check(ast)
        self.assertEqual(len(errors), 0, "DSL pattern should type check correctly")

if __name__ == "__main__":
    unittest.main()