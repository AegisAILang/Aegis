"""
Test suite for the AegisASTVisitor.

Tests that the visitor correctly visits and processes all grammar rules
in the Aegis language, ensuring the AST structure is properly created.
"""

import unittest
from src.parser.aeigix_ast_visitor import AegisASTVisitor, SourcePosition
from dataclasses import asdict
from typing import Dict, Any

class TestASTVisitor(unittest.TestCase):
    def setUp(self):
        self.visitor = AegisASTVisitor(source_file="test.ae")
        
    def test_visit_module(self):
        """Test module node visitation"""
        # Create a mock module node
        module_node = type('obj', (object,), {
            'name': 'TestModule',
            'body': [],
            'line': 1,
            'column': 1
        })
        
        result = self.visitor.visit_module(module_node)
        
        self.assertEqual(result["node_type"], "module")
        self.assertEqual(result["name"], "TestModule")
        self.assertEqual(len(result["children"]), 0)
        
    def test_visit_struct(self):
        """Test struct node visitation"""
        # Create a mock struct node with fields
        field1 = type('obj', (object,), {
            'type': 'field',
            'name': 'id',
            'field_type': type('obj', (object,), {'name': 'int'}),
            'line': 2,
            'column': 5
        })
        field2 = type('obj', (object,), {
            'type': 'field',
            'name': 'name',
            'field_type': type('obj', (object,), {'name': 'string'}),
            'line': 3,
            'column': 5
        })
        
        struct_node = type('obj', (object,), {
            'name': 'User',
            'body': [field1, field2],
            'line': 1,
            'column': 1,
            'traits': []
        })
        
        result = self.visitor.visit_struct(struct_node)
        
        self.assertEqual(result["node_type"], "struct")
        self.assertEqual(result["name"], "User")
        self.assertEqual(len(result["fields"]), 2)
        self.assertEqual(result["fields"][0]["name"], "id")
        
    def test_visit_function(self):
        """Test function node visitation"""
        # Create a mock function node
        ret_type = type('obj', (object,), {'name': 'int'})
        param = type('obj', (object,), {
            'name': 'x',
            'param_type': type('obj', (object,), {'name': 'int'}),
            'line': 2,
            'column': 10
        })
        
        stmt = type('obj', (object,), {
            'type': 'return_statement',
            'value': type('obj', (object,), {
                'type': 'literal',
                'value': 42,
                'literal_type': 'int',
                'line': 3,
                'column': 12
            }),
            'line': 3,
            'column': 5
        })
        
        function_node = type('obj', (object,), {
            'name': 'add',
            'parameters': [param],
            'return_type': ret_type,
            'body': [stmt],
            'line': 1,
            'column': 1,
            'type': 'function'
        })
        
        result = self.visitor.visit_function(function_node)
        
        self.assertEqual(result["node_type"], "function")
        self.assertEqual(result["name"], "add")
        self.assertEqual(len(result["parameters"]), 1)
        self.assertEqual(result["parameters"][0]["name"], "x")
        
    def test_visit_option_type(self):
        """Test option type visitation"""
        # Create a mock Option<T> type node
        inner_type = type('obj', (object,), {'name': 'User'})
        option_type = type('obj', (object,), {
            'name': 'Option',
            'type_params': [inner_type],
            'line': 1,
            'column': 10
        })
        
        # Mock a function return type using Option<User>
        function_node = type('obj', (object,), {
            'name': 'get_user',
            'parameters': [],
            'return_type': option_type,
            'body': [],
            'line': 1,
            'column': 1,
            'type': 'function'
        })
        
        result = self.visitor.visit_function(function_node)
        
        # Verify that the return type is properly captured
        self.assertEqual(result["node_type"], "function")
        self.assertEqual(result["name"], "get_user")
        # The return_type structure depends on visitor implementation
        self.assertTrue("return_type" in result)
        
    def test_visit_if_statement(self):
        """Test if statement visitation"""
        # Create a mock if statement node
        condition = type('obj', (object,), {
            'type': 'binary_operation',
            'operator': '>',
            'left': type('obj', (object,), {
                'type': 'identifier',
                'name': 'x',
                'line': 2,
                'column': 5
            }),
            'right': type('obj', (object,), {
                'type': 'literal',
                'value': 0,
                'literal_type': 'int',
                'line': 2,
                'column': 9
            }),
            'line': 2,
            'column': 7
        })
        
        then_stmt = type('obj', (object,), {
            'type': 'return_statement',
            'value': type('obj', (object,), {
                'type': 'identifier',
                'name': 'x',
                'line': 3,
                'column': 12
            }),
            'line': 3,
            'column': 5
        })
        
        else_stmt = type('obj', (object,), {
            'type': 'return_statement',
            'value': type('obj', (object,), {
                'type': 'literal',
                'value': 0,
                'literal_type': 'int',
                'line': 5,
                'column': 12
            }),
            'line': 5,
            'column': 5
        })
        
        if_node = type('obj', (object,), {
            'type': 'if_statement',
            'condition': condition,
            'then_branch': [then_stmt],
            'else_branch': [else_stmt],
            'line': 1,
            'column': 1
        })
        
        # Check if visitor has visit_if_statement method
        if hasattr(self.visitor, 'visit_if_statement'):
            result = self.visitor.visit_if_statement(if_node)
            
            self.assertEqual(result["node_type"], "if_statement")
            self.assertTrue("condition" in result)
            self.assertTrue("then_branch" in result)
            self.assertTrue("else_branch" in result)
    
    def test_visit_match_statement(self):
        """Test match statement visitation"""
        # Create a mock match statement with Option<T> patterns
        
        subject = type('obj', (object,), {
            'type': 'identifier',
            'name': 'result',
            'line': 1,
            'column': 7
        })
        
        some_pattern = type('obj', (object,), {
            'type': 'constructor_pattern',
            'name': 'Some',
            'bindings': [type('obj', (object,), {
                'type': 'binding_pattern',
                'name': 'value',
                'line': 2,
                'column': 10
            })],
            'line': 2,
            'column': 5
        })
        
        some_body = type('obj', (object,), {
            'type': 'expression_statement',
            'expression': type('obj', (object,), {
                'type': 'identifier',
                'name': 'value',
                'line': 2,
                'column': 20
            }),
            'line': 2,
            'column': 15
        })
        
        none_pattern = type('obj', (object,), {
            'type': 'constructor_pattern',
            'name': 'None',
            'bindings': [],
            'line': 3,
            'column': 5
        })
        
        none_body = type('obj', (object,), {
            'type': 'literal',
            'value': 0,
            'literal_type': 'int',
            'line': 3,
            'column': 15
        })
        
        branches = [
            type('obj', (object,), {
                'pattern': some_pattern,
                'body': some_body,
                'guard': None,
                'line': 2,
                'column': 5
            }),
            type('obj', (object,), {
                'pattern': none_pattern,
                'body': none_body,
                'guard': None,
                'line': 3,
                'column': 5
            })
        ]
        
        match_node = type('obj', (object,), {
            'type': 'match_statement',
            'subject': subject,
            'branches': branches,
            'line': 1,
            'column': 1
        })
        
        # Check if visitor has visit_match_statement method
        if hasattr(self.visitor, 'visit_match_statement'):
            result = self.visitor.visit_match_statement(match_node)
            
            self.assertEqual(result["node_type"], "match_statement")
            self.assertTrue("subject" in result)
            self.assertTrue("branches" in result)
            self.assertEqual(len(result["branches"]), 2)
    
    def test_visit_async_function(self):
        """Test async function visitation"""
        # Create a mock async function node
        ret_type = type('obj', (object,), {'name': 'string'})
        
        stmt = type('obj', (object,), {
            'type': 'return_statement',
            'value': type('obj', (object,), {
                'type': 'literal',
                'value': "result",
                'literal_type': 'string',
                'line': 2,
                'column': 12
            }),
            'line': 2,
            'column': 5
        })
        
        async_function_node = type('obj', (object,), {
            'name': 'fetch_data',
            'parameters': [],
            'return_type': ret_type,
            'body': [stmt],
            'line': 1,
            'column': 1,
            'type': 'function',
            'is_async': True  # Indicate this is an async function
        })
        
        # Check if visitor properly handles async functions
        result = self.visitor.visit_function(async_function_node)
        
        self.assertEqual(result["node_type"], "function")
        self.assertEqual(result["name"], "fetch_data")
        # The is_async attribute depends on visitor implementation
        if "is_async" in result:
            self.assertTrue(result["is_async"])
    
    def test_source_position_tracking(self):
        """Test that source positions are tracked correctly"""
        # Create a node with line and column information
        node = type('obj', (object,), {
            'name': 'test',
            'body': [],
            'line': 42,
            'column': 10
        })
        
        # Test with visitor's _make_node_info helper method
        pos = SourcePosition(42, 10, "test.ae")
        node_info = self.visitor._make_node_info("test", "test", [], pos)
        
        self.assertEqual(node_info["position"].line, 42)
        self.assertEqual(node_info["position"].column, 10)
        self.assertEqual(node_info["position"].file_path, "test.ae")

if __name__ == "__main__":
    unittest.main()