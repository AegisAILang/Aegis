"""
Test suite for the LLVM code generation in Aegis.

Tests the generation of LLVM IR code for various Aegis language constructs,
ensuring that the output is correct and can be compiled/executed.
"""

import unittest
import tempfile
import os
import subprocess
from src.codegen.llvm_generator import LLVMGenerator, WasmGenerator
from src.parser.aeigix_ast_visitor import SourcePosition, AegisASTVisitor
from llvmlite import binding

# Initialize LLVM
binding.initialize()
binding.initialize_native_target()
binding.initialize_native_asmprinter()

class TestLLVMCodeGen(unittest.TestCase):
    def setUp(self):
        # Create a simple mock for the target machine
        self.target = binding.Target.from_default_triple()
        self.target_machine = self.target.create_target_machine()
    
    def test_basic_function_generation(self):
        """Test generation of a basic function"""
        # Create a simple AST for a function that returns an integer
        ast = {
            "node_type": "module",
            "name": "Test",
            "children": [{
                "node_type": "function",
                "name": "add",
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
                "return_type": {"name": "int"},
                "body": [{
                    "node_type": "return_statement",
                    "value": {
                        "node_type": "binary_operation",
                        "operator": "+",
                        "left": {
                            "node_type": "identifier",
                            "name": "a",
                            "position": SourcePosition(2, 12, "test.ae")
                        },
                        "right": {
                            "node_type": "identifier",
                            "name": "b",
                            "position": SourcePosition(2, 16, "test.ae")
                        },
                        "position": SourcePosition(2, 14, "test.ae")
                    },
                    "position": SourcePosition(2, 5, "test.ae")
                }],
                "position": SourcePosition(1, 1, "test.ae")
            }],
            "position": SourcePosition(1, 1, "test.ae")
        }
        
        # Generate LLVM IR
        generator = LLVMGenerator(ast)
        ir_code = generator.generate()
        
        # Verify the IR is valid
        module = binding.parse_assembly(ir_code)
        module.verify()
        
        # Check for key elements in the generated IR
        self.assertIn("define", ir_code)
        self.assertIn("add", ir_code)
        self.assertIn("add", ir_code)
        
    def test_struct_generation(self):
        """Test generation of a struct with fields"""
        # Create an AST for a struct definition
        ast = {
            "node_type": "module",
            "name": "Test",
            "children": [{
                "node_type": "struct",
                "name": "Point",
                "fields": [
                    {
                        "node_type": "field",
                        "name": "x",
                        "field_type": {"name": "int"},
                        "position": SourcePosition(2, 5, "test.ae")
                    },
                    {
                        "node_type": "field",
                        "name": "y",
                        "field_type": {"name": "int"},
                        "position": SourcePosition(3, 5, "test.ae")
                    }
                ],
                "methods": [],
                "position": SourcePosition(1, 1, "test.ae")
            }],
            "position": SourcePosition(1, 1, "test.ae")
        }
        
        # Generate LLVM IR
        generator = LLVMGenerator(ast)
        ir_code = generator.generate()
        
        # Verify the IR is valid
        module = binding.parse_assembly(ir_code)
        module.verify()
        
        # Check for struct type definition
        self.assertIn("type %Point", ir_code.replace(" ", ""))
        
    def test_conditional_code_generation(self):
        """Test generation of if-else statements"""
        # Create an AST with an if-else statement
        ast = {
            "node_type": "module",
            "name": "Test",
            "children": [{
                "node_type": "function",
                "name": "max",
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
                "return_type": {"name": "int"},
                "body": [{
                    "node_type": "if_statement",
                    "condition": {
                        "node_type": "binary_operation",
                        "operator": ">",
                        "left": {
                            "node_type": "identifier",
                            "name": "a",
                            "position": SourcePosition(2, 9, "test.ae")
                        },
                        "right": {
                            "node_type": "identifier",
                            "name": "b",
                            "position": SourcePosition(2, 13, "test.ae")
                        },
                        "position": SourcePosition(2, 11, "test.ae")
                    },
                    "then_branch": [{
                        "node_type": "return_statement",
                        "value": {
                            "node_type": "identifier",
                            "name": "a",
                            "position": SourcePosition(3, 16, "test.ae")
                        },
                        "position": SourcePosition(3, 9, "test.ae")
                    }],
                    "else_branch": [{
                        "node_type": "return_statement",
                        "value": {
                            "node_type": "identifier",
                            "name": "b",
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
        
        # Generate LLVM IR
        generator = LLVMGenerator(ast)
        ir_code = generator.generate()
        
        # Verify the IR contains branching instructions
        self.assertIn("icmp", ir_code)
        self.assertIn("br", ir_code)
        
    def test_option_type_generation(self):
        """Test generation of Option<T> pattern"""
        # Create an AST with Option<T> usage
        ast = {
            "node_type": "module",
            "name": "Test",
            "children": [{
                "node_type": "function",
                "name": "find_value",
                "parameters": [
                    {
                        "name": "key",
                        "param_type": {"name": "int"},
                        "position": SourcePosition(1, 15, "test.ae")
                    }
                ],
                "return_type": {
                    "name": "Option",
                    "type_params": [{"name": "int"}],
                    "position": SourcePosition(1, 35, "test.ae")
                },
                "body": [{
                    "node_type": "if_statement",
                    "condition": {
                        "node_type": "binary_operation",
                        "operator": ">",
                        "left": {
                            "node_type": "identifier",
                            "name": "key",
                            "position": SourcePosition(2, 9, "test.ae")
                        },
                        "right": {
                            "node_type": "literal",
                            "literal_type": "int",
                            "value": 0,
                            "position": SourcePosition(2, 15, "test.ae")
                        },
                        "position": SourcePosition(2, 13, "test.ae")
                    },
                    "then_branch": [{
                        "node_type": "return_statement",
                        "value": {
                            "node_type": "constructor_call",
                            "name": "Some",
                            "arguments": [{
                                "node_type": "identifier",
                                "name": "key",
                                "position": SourcePosition(3, 21, "test.ae")
                            }],
                            "position": SourcePosition(3, 16, "test.ae")
                        },
                        "position": SourcePosition(3, 9, "test.ae")
                    }],
                    "else_branch": [{
                        "node_type": "return_statement",
                        "value": {
                            "node_type": "constructor_call",
                            "name": "None",
                            "arguments": [],
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
        
        # Generate LLVM IR
        generator = LLVMGenerator(ast)
        ir_code = generator.generate()
        
        # Check if the IR compiles successfully
        module = binding.parse_assembly(ir_code)
        module.verify()
        
    def test_loop_generation(self):
        """Test generation of loop constructs"""
        # Create an AST with a while loop
        ast = {
            "node_type": "module",
            "name": "Test",
            "children": [{
                "node_type": "function",
                "name": "sum_to_n",
                "parameters": [
                    {
                        "name": "n",
                        "param_type": {"name": "int"},
                        "position": SourcePosition(1, 15, "test.ae")
                    }
                ],
                "return_type": {"name": "int"},
                "body": [
                    {
                        "node_type": "variable_declaration",
                        "name": "sum",
                        "var_type": {"name": "int"},
                        "init_value": {
                            "node_type": "literal",
                            "literal_type": "int",
                            "value": 0,
                            "position": SourcePosition(2, 14, "test.ae")
                        },
                        "position": SourcePosition(2, 5, "test.ae")
                    },
                    {
                        "node_type": "variable_declaration",
                        "name": "i",
                        "var_type": {"name": "int"},
                        "init_value": {
                            "node_type": "literal",
                            "literal_type": "int",
                            "value": 1,
                            "position": SourcePosition(3, 12, "test.ae")
                        },
                        "position": SourcePosition(3, 5, "test.ae")
                    },
                    {
                        "node_type": "while_statement",
                        "condition": {
                            "node_type": "binary_operation",
                            "operator": "<=",
                            "left": {
                                "node_type": "identifier",
                                "name": "i",
                                "position": SourcePosition(4, 12, "test.ae")
                            },
                            "right": {
                                "node_type": "identifier",
                                "name": "n",
                                "position": SourcePosition(4, 17, "test.ae")
                            },
                            "position": SourcePosition(4, 14, "test.ae")
                        },
                        "body": [
                            {
                                "node_type": "expression_statement",
                                "expression": {
                                    "node_type": "binary_operation",
                                    "operator": "=",
                                    "left": {
                                        "node_type": "identifier",
                                        "name": "sum",
                                        "position": SourcePosition(5, 9, "test.ae")
                                    },
                                    "right": {
                                        "node_type": "binary_operation",
                                        "operator": "+",
                                        "left": {
                                            "node_type": "identifier",
                                            "name": "sum",
                                            "position": SourcePosition(5, 15, "test.ae")
                                        },
                                        "right": {
                                            "node_type": "identifier",
                                            "name": "i",
                                            "position": SourcePosition(5, 21, "test.ae")
                                        },
                                        "position": SourcePosition(5, 19, "test.ae")
                                    },
                                    "position": SourcePosition(5, 13, "test.ae")
                                },
                                "position": SourcePosition(5, 9, "test.ae")
                            },
                            {
                                "node_type": "expression_statement",
                                "expression": {
                                    "node_type": "binary_operation",
                                    "operator": "=",
                                    "left": {
                                        "node_type": "identifier",
                                        "name": "i",
                                        "position": SourcePosition(6, 9, "test.ae")
                                    },
                                    "right": {
                                        "node_type": "binary_operation",
                                        "operator": "+",
                                        "left": {
                                            "node_type": "identifier",
                                            "name": "i",
                                            "position": SourcePosition(6, 13, "test.ae")
                                        },
                                        "right": {
                                            "node_type": "literal",
                                            "literal_type": "int",
                                            "value": 1,
                                            "position": SourcePosition(6, 17, "test.ae")
                                        },
                                        "position": SourcePosition(6, 15, "test.ae")
                                    },
                                    "position": SourcePosition(6, 11, "test.ae")
                                },
                                "position": SourcePosition(6, 9, "test.ae")
                            }
                        ],
                        "position": SourcePosition(4, 5, "test.ae")
                    },
                    {
                        "node_type": "return_statement",
                        "value": {
                            "node_type": "identifier",
                            "name": "sum",
                            "position": SourcePosition(8, 12, "test.ae")
                        },
                        "position": SourcePosition(8, 5, "test.ae")
                    }
                ],
                "position": SourcePosition(1, 1, "test.ae")
            }],
            "position": SourcePosition(1, 1, "test.ae")
        }
        
        # Generate LLVM IR
        generator = LLVMGenerator(ast)
        ir_code = generator.generate()
        
        # Verify that the IR contains loop constructs
        self.assertIn("br", ir_code)
        self.assertIn("icmp", ir_code)
        
    def test_result_type_generation(self):
        """Test generation of Result<T, E> pattern"""
        # Create an AST with Result<T, E> usage
        ast = {
            "node_type": "module",
            "name": "Test",
            "children": [{
                "node_type": "function",
                "name": "safe_divide",
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
        
        # Generate LLVM IR
        generator = LLVMGenerator(ast)
        ir_code = generator.generate()
        
        # Verify the IR is valid
        module = binding.parse_assembly(ir_code)
        module.verify()
        
    def test_match_expression_generation(self):
        """Test generation of match expression"""
        # Create an AST with a match expression
        ast = {
            "node_type": "module",
            "name": "Test",
            "children": [{
                "node_type": "function",
                "name": "process_option",
                "parameters": [
                    {
                        "name": "opt",
                        "param_type": {
                            "name": "Option",
                            "type_params": [{"name": "int"}],
                            "position": SourcePosition(1, 25, "test.ae")
                        },
                        "position": SourcePosition(1, 20, "test.ae")
                    }
                ],
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
                        },
                        {
                            "pattern": {
                                "node_type": "constructor_pattern",
                                "name": "None",
                                "bindings": [],
                                "position": SourcePosition(4, 5, "test.ae")
                            },
                            "body": {
                                "node_type": "return_statement",
                                "value": {
                                    "node_type": "literal",
                                    "literal_type": "int",
                                    "value": 0,
                                    "position": SourcePosition(4, 25, "test.ae")
                                },
                                "position": SourcePosition(4, 18, "test.ae")
                            },
                            "guard": None
                        }
                    ],
                    "position": SourcePosition(2, 5, "test.ae")
                }],
                "position": SourcePosition(1, 1, "test.ae")
            }],
            "position": SourcePosition(1, 1, "test.ae")
        }
        
        # Generate LLVM IR
        generator = LLVMGenerator(ast)
        ir_code = generator.generate()
        
        # Verify the IR contains pattern matching constructs
        self.assertIn("switch", ir_code)
        
    def test_wasm_generation(self):
        """Test WebAssembly compatible IR generation"""
        # Create a simple AST
        ast = {
            "node_type": "module",
            "name": "WasmTest",
            "children": [{
                "node_type": "function",
                "name": "add",
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
                "return_type": {"name": "int"},
                "body": [{
                    "node_type": "return_statement",
                    "value": {
                        "node_type": "binary_operation",
                        "operator": "+",
                        "left": {
                            "node_type": "identifier",
                            "name": "a",
                            "position": SourcePosition(2, 12, "test.ae")
                        },
                        "right": {
                            "node_type": "identifier",
                            "name": "b",
                            "position": SourcePosition(2, 16, "test.ae")
                        },
                        "position": SourcePosition(2, 14, "test.ae")
                    },
                    "position": SourcePosition(2, 5, "test.ae")
                }],
                "position": SourcePosition(1, 1, "test.ae")
            }],
            "position": SourcePosition(1, 1, "test.ae")
        }
        
        # Generate WebAssembly-compatible IR
        generator = WasmGenerator(ast)
        ir_code = generator.generate()
        
        # Verify that the module has WASM target triple
        self.assertIn("wasm32-unknown-unknown", ir_code)
        
        # Verify that int types are 32-bit (WebAssembly prefers 32-bit integers)
        self.assertIn("i32", ir_code)
        
    def test_dsl_pattern_generation(self):
        """Test generation of DSL-like pattern"""
        # Create an AST with a DSL-like pattern for a query builder
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
                    }
                ],
                "methods": [],
                "position": SourcePosition(1, 1, "test.ae")
            }, {
                "node_type": "function",
                "name": "select",
                "parameters": [{
                    "name": "fields",
                    "param_type": {"name": "string"},
                    "position": SourcePosition(5, 15, "test.ae")
                }],
                "return_type": {"name": "Query"},
                "body": [{
                    "node_type": "variable_declaration",
                    "name": "query",
                    "var_type": {"name": "Query"},
                    "init_value": {
                        "node_type": "constructor_call",
                        "name": "Query",
                        "arguments": [{
                            "node_type": "literal",
                            "literal_type": "string",
                            "value": "",
                            "position": SourcePosition(6, 20, "test.ae")
                        }],
                        "position": SourcePosition(6, 14, "test.ae")
                    },
                    "position": SourcePosition(6, 5, "test.ae")
                }, {
                    "node_type": "return_statement",
                    "value": {
                        "node_type": "identifier",
                        "name": "query",
                        "position": SourcePosition(7, 12, "test.ae")
                    },
                    "position": SourcePosition(7, 5, "test.ae")
                }],
                "position": SourcePosition(5, 1, "test.ae")
            }],
            "position": SourcePosition(1, 1, "test.ae")
        }
        
        # Generate LLVM IR for DSL pattern
        generator = LLVMGenerator(ast)
        ir_code = generator.generate()
        
        # Verify the IR is valid
        module = binding.parse_assembly(ir_code)
        module.verify()
        
        # Verify struct type and function
        self.assertIn("type %Query", ir_code.replace(" ", ""))
        self.assertIn("define", ir_code)
        self.assertIn("select", ir_code)

if __name__ == "__main__":
    unittest.main()