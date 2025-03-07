from typing import Dict, List, Any, Optional, Union, Set
from dataclasses import dataclass
from src.parser.aeigix_ast_visitor import SourcePosition
from src.semantic.symbol_table import SymbolTable, Symbol, SymbolType, Scope
import logging

logger = logging.getLogger(__name__)

@dataclass
class TypeCheckError:
    """Represents a type checking error with a helpful message and suggestion."""
    message: str
    suggestion: str
    position: SourcePosition
    
    def __str__(self) -> str:
        return f"{self.position}: Error: {self.message}\nSuggestion: {self.suggestion}"

class TypeChecker:
    """
    Type checker for Aegis programming language.
    
    Performs semantic analysis to ensure type safety, verify all symbols are defined,
    and confirm that functions with non-void return types return values on all code paths.
    
    Provides detailed, AI-friendly error messages with suggestions for fixing issues.
    """
    
    def __init__(self):
        self.symbol_table = SymbolTable()
        self.errors = []
        self.current_function = None
        self.current_function_returns = False
        self.in_loop = False
    
    def check(self, ast: Dict[str, Any]) -> List[TypeCheckError]:
        """
        Perform type checking on the entire AST.
        
        Args:
            ast: The AST to check
            
        Returns:
            List of type checking errors
        """
        logger.info("Starting type checking")
        
        # Clear any previous state
        self.symbol_table = SymbolTable()
        self.errors = []
        
        # First pass: register all top-level declarations
        self._register_declarations(ast)
        
        # Second pass: validate all declarations and check for type errors
        self._check_node(ast)
        
        if not self.errors:
            logger.info("Type checking completed successfully")
        else:
            logger.error(f"Type checking failed with {len(self.errors)} errors")
            
        return self.errors
    
    def _register_declarations(self, node: Dict[str, Any]) -> None:
        """
        First pass to register all declarations in the symbol table.
        
        This establishes all available types, functions, and variables before
        checking their implementations, which helps with forward references.
        
        Args:
            node: The AST node to process
        """
        if node is None:
            return
            
        node_type = node.get("node_type", "")
        
        if node_type == "module":
            # Register the module and process its children
            module_name = node["name"]
            self.symbol_table.enter_scope(module_name)
            
            for child in node.get("children", []):
                self._register_declarations(child)
                
            self.symbol_table.exit_scope()
            
        elif node_type == "struct":
            # Register the struct type
            struct_name = node["name"]
            fields = {}
            
            for field in node.get("fields", []):
                field_name = field["name"]
                field_type = field["type_annotation"]["name"]
                fields[field_name] = field_type
                
            self.symbol_table.add_symbol(
                name=struct_name,
                symbol_type=SymbolType.TYPE,
                type_info={
                    "kind": "struct",
                    "fields": fields
                }
            )
            
            # Process method declarations
            for method in node.get("methods", []):
                self._register_declarations(method)
                
        elif node_type == "enum":
            # Register the enum type
            enum_name = node["name"]
            variants = {}
            
            for variant in node.get("variants", []):
                variant_name = variant["name"]
                variant_fields = {}
                
                for field in variant.get("fields", []):
                    field_name = field["name"] if "name" in field else ""
                    field_type = field["type_annotation"]["name"]
                    variant_fields[field_name] = field_type
                
                variants[variant_name] = variant_fields
                
            self.symbol_table.add_symbol(
                name=enum_name,
                symbol_type=SymbolType.TYPE,
                type_info={
                    "kind": "enum",
                    "variants": variants
                }
            )
            
            # Process method declarations
            for method in node.get("methods", []):
                self._register_declarations(method)
                
        elif node_type == "function":
            # Register the function signature
            func_name = node["name"]
            params = []
            
            for param in node.get("params", []):
                param_name = param["name"]
                param_type = param["type_annotation"]["name"] if param.get("type_annotation") else "any"
                params.append((param_name, param_type))
                
            return_type = node.get("return_type", {}).get("name", "void")
            
            self.symbol_table.add_symbol(
                name=func_name,
                symbol_type=SymbolType.FUNCTION,
                type_info={
                    "params": params,
                    "return_type": return_type,
                    "is_async": node.get("is_async", False)
                }
            )
            
        elif node_type == "trait":
            # Register the trait
            trait_name = node["name"]
            methods = {}
            
            for method in node.get("methods", []):
                method_name = method["name"]
                params = []
                
                for param in method.get("params", []):
                    param_name = param["name"]
                    param_type = param["type_annotation"]["name"] if param.get("type_annotation") else "any"
                    params.append((param_name, param_type))
                    
                return_type = method.get("return_type", {}).get("name", "void")
                
                methods[method_name] = {
                    "params": params,
                    "return_type": return_type,
                    "is_async": method.get("is_async", False)
                }
                
            self.symbol_table.add_symbol(
                name=trait_name,
                symbol_type=SymbolType.TRAIT,
                type_info={
                    "methods": methods
                }
            )
    
    def _check_node(self, node: Dict[str, Any]) -> Optional[str]:
        """
        Check a node for type errors and validate its children.
        
        Args:
            node: The AST node to check
            
        Returns:
            The type of the expression, if applicable
        """
        if node is None:
            return None
            
        node_type = node.get("node_type", "")
        position = node.get("position", SourcePosition(0, 0, ""))
        
        # Handle each node type
        if node_type == "module":
            module_name = node["name"]
            self.symbol_table.enter_scope(module_name)
            
            for child in node.get("children", []):
                self._check_node(child)
                
            self.symbol_table.exit_scope()
            
        elif node_type == "struct":
            struct_name = node["name"]
            self.symbol_table.enter_scope(struct_name)
            
            # Check field types exist
            for field in node.get("fields", []):
                field_type_name = field["type_annotation"]["name"]
                if not self._is_valid_type(field_type_name):
                    self.errors.append(TypeCheckError(
                        message=f"Field '{field['name']}' has undefined type '{field_type_name}'",
                        suggestion=f"Use a valid type like 'int', 'string', or define the struct '{field_type_name}' before using it",
                        position=field["position"]
                    ))
            
            # Check methods
            for method in node.get("methods", []):
                self._check_node(method)
                
            self.symbol_table.exit_scope()
            
        elif node_type == "enum":
            enum_name = node["name"]
            self.symbol_table.enter_scope(enum_name)
            
            # Check variant field types exist
            for variant in node.get("variants", []):
                for field in variant.get("fields", []):
                    field_type_name = field["type_annotation"]["name"]
                    if not self._is_valid_type(field_type_name):
                        self.errors.append(TypeCheckError(
                            message=f"Variant field '{field['name']}' has undefined type '{field_type_name}'",
                            suggestion=f"Use a valid type like 'int', 'string', or define the type '{field_type_name}' before using it",
                            position=field["position"]
                        ))
            
            # Check methods
            for method in node.get("methods", []):
                self._check_node(method)
                
            self.symbol_table.exit_scope()
            
        elif node_type == "function":
            func_name = node["name"]
            self.current_function = node
            self.current_function_returns = False
            
            # Check return type exists
            return_type = node.get("return_type", {}).get("name", "void")
            if return_type != "void" and not self._is_valid_type(return_type):
                self.errors.append(TypeCheckError(
                    message=f"Function '{func_name}' has undefined return type '{return_type}'",
                    suggestion=f"Use a valid type like 'int', 'string', or define the type '{return_type}' before using it",
                    position=node["position"]
                ))
            
            # Enter function scope
            self.symbol_table.enter_scope(func_name)
            
            # Add parameters to scope
            for param in node.get("params", []):
                param_name = param["name"]
                param_type = param["type_annotation"]["name"] if param.get("type_annotation") else "any"
                
                # Check parameter type exists
                if not self._is_valid_type(param_type):
                    self.errors.append(TypeCheckError(
                        message=f"Parameter '{param_name}' has undefined type '{param_type}'",
                        suggestion=f"Use a valid type like 'int', 'string', or define the type '{param_type}' before using it",
                        position=param["position"]
                    ))
                
                self.symbol_table.add_symbol(
                    name=param_name,
                    symbol_type=SymbolType.VARIABLE,
                    type_info=param_type
                )
            
            # Check function body
            for stmt in node.get("body", []):
                self._check_node(stmt)
            
            # Check if function returns a value on all paths if non-void
            if return_type != "void" and not self.current_function_returns:
                self.errors.append(TypeCheckError(
                    message=f"Function '{func_name}' must return a value of type '{return_type}' on all code paths",
                    suggestion="Add a return statement with the appropriate value type at the end of the function",
                    position=node["position"]
                ))
            
            self.symbol_table.exit_scope()
            self.current_function = None
            
        elif node_type == "var_declaration":
            var_name = node["name"]
            var_type = node["type_annotation"]["name"] if node.get("type_annotation") else None
            
            # Check if the variable type exists
            if var_type and not self._is_valid_type(var_type):
                self.errors.append(TypeCheckError(
                    message=f"Variable '{var_name}' has undefined type '{var_type}'",
                    suggestion=f"Use a valid type like 'int', 'string', or define the type '{var_type}' before using it",
                    position=node["position"]
                ))
            
            # Check initialization value type
            init_value = node.get("init_value")
            if init_value:
                init_type = self._check_node(init_value)
                
                if var_type and init_type and not self._are_types_compatible(var_type, init_type):
                    self.errors.append(TypeCheckError(
                        message=f"Cannot assign value of type '{init_type}' to variable '{var_name}' of type '{var_type}'",
                        suggestion=f"Use a value of type '{var_type}' or convert the value to '{var_type}'",
                        position=node["position"]
                    ))
                
                # Infer type if not specified
                if not var_type and init_type:
                    var_type = init_type
            
            # Add variable to symbol table
            self.symbol_table.add_symbol(
                name=var_name,
                symbol_type=SymbolType.VARIABLE,
                type_info=var_type or "any"
            )
            
            return var_type
            
        elif node_type == "assignment":
            target = node["target"]
            target_type = self._check_node(target)
            
            value = node["value"]
            value_type = self._check_node(value)
            
            # Check if types are compatible
            if target_type and value_type and not self._are_types_compatible(target_type, value_type):
                target_name = target.get("name", "expression")
                self.errors.append(TypeCheckError(
                    message=f"Cannot assign value of type '{value_type}' to target of type '{target_type}'",
                    suggestion=f"Use a value of type '{target_type}' or convert the value to '{target_type}'",
                    position=node["position"]
                ))
            
            # Check if target is immutable (let)
            if target.get("node_type") == "identifier":
                symbol = self.symbol_table.lookup(target["name"])
                if symbol and hasattr(symbol, "is_mutable") and not symbol.is_mutable:
                    self.errors.append(TypeCheckError(
                        message=f"Cannot assign to immutable variable '{target['name']}'",
                        suggestion="Use 'var' instead of 'let' if the variable needs to be mutable",
                        position=node["position"]
                    ))
            
            return target_type
            
        elif node_type == "binary_op":
            left_type = self._check_node(node["left"])
            right_type = self._check_node(node["right"])
            operator = node["operator"]
            
            # Check operator compatibility
            result_type = self._check_binary_op_types(left_type, right_type, operator, node["position"])
            return result_type
            
        elif node_type == "unary_op":
            operand_type = self._check_node(node["operand"])
            operator = node["operator"]
            
            # Check operator compatibility
            result_type = self._check_unary_op_types(operand_type, operator, node["position"])
            return result_type
            
        elif node_type == "call":
            callee = node["callee"]
            callee_type = self._check_node(callee)
            
            # Handle method calls and function calls differently
            if callee.get("node_type") == "member_access":
                return self._check_method_call(callee, node.get("args", []), node["position"])
            else:
                return self._check_function_call(callee["name"] if "name" in callee else "", node.get("args", []), node["position"])
            
        elif node_type == "if_statement":
            # Check condition is boolean
            condition_type = self._check_node(node["condition"])
            if condition_type and condition_type != "bool":
                self.errors.append(TypeCheckError(
                    message=f"If condition must be a boolean, got '{condition_type}'",
                    suggestion="Use a comparison or logical expression that evaluates to a boolean",
                    position=node["position"]
                ))
            
            # Check branches
            self.symbol_table.enter_scope("if_branch")
            self._check_node(node["then_block"])
            self.symbol_table.exit_scope()
            
            if node.get("else_block"):
                self.symbol_table.enter_scope("else_branch")
                self._check_node(node["else_block"])
                self.symbol_table.exit_scope()
            
            # Check elif branches
            for branch in node.get("elif_branches", []):
                elif_condition_type = self._check_node(branch["condition"])
                if elif_condition_type and elif_condition_type != "bool":
                    self.errors.append(TypeCheckError(
                        message=f"Elif condition must be a boolean, got '{elif_condition_type}'",
                        suggestion="Use a comparison or logical expression that evaluates to a boolean",
                        position=branch["condition"]["position"]
                    ))
                
                self.symbol_table.enter_scope("elif_branch")
                self._check_node(branch["block"])
                self.symbol_table.exit_scope()
            
        elif node_type == "for_loop":
            self.in_loop = True
            
            # Check iterable is actually iterable
            iterable_type = self._check_node(node["iterable"])
            element_type = self._get_element_type(iterable_type)
            
            if not element_type:
                self.errors.append(TypeCheckError(
                    message=f"Cannot iterate over type '{iterable_type}'",
                    suggestion="Use a collection type like an array, range, or implement the Iterable trait",
                    position=node["iterable"]["position"]
                ))
            
            # Set up loop variable in new scope
            self.symbol_table.enter_scope("for_loop")
            iterator_name = node["iterator"]["name"] if node["iterator"].get("node_type") == "var_declaration" else node["iterator"]["name"]
            
            self.symbol_table.add_symbol(
                name=iterator_name,
                symbol_type=SymbolType.VARIABLE,
                type_info=element_type or "any"
            )
            
            # Check loop body
            self._check_node(node["body"])
            
            self.symbol_table.exit_scope()
            self.in_loop = False
            
        elif node_type == "while_loop":
            self.in_loop = True
            
            # Check condition is boolean
            condition_type = self._check_node(node["condition"])
            if condition_type and condition_type != "bool":
                self.errors.append(TypeCheckError(
                    message=f"While condition must be a boolean, got '{condition_type}'",
                    suggestion="Use a comparison or logical expression that evaluates to a boolean",
                    position=node["condition"]["position"]
                ))
            
            # Check loop body
            self.symbol_table.enter_scope("while_loop")
            self._check_node(node["body"])
            self.symbol_table.exit_scope()
            
            self.in_loop = False
            
        elif node_type == "return_statement":
            # Mark that this function has a return statement
            self.current_function_returns = True
            
            # Check return type matches function return type
            if self.current_function:
                expected_type = self.current_function.get("return_type", {}).get("name", "void")
                
                if expected_type == "void" and node.get("value"):
                    self.errors.append(TypeCheckError(
                        message="Cannot return a value from a function with void return type",
                        suggestion="Remove the return value or change the function return type",
                        position=node["position"]
                    ))
                elif expected_type != "void":
                    if not node.get("value"):
                        self.errors.append(TypeCheckError(
                            message=f"Function expects return value of type '{expected_type}' but no value is returned",
                            suggestion=f"Add a return value of type '{expected_type}'",
                            position=node["position"]
                        ))
                    else:
                        actual_type = self._check_node(node["value"])
                        if actual_type and not self._are_types_compatible(expected_type, actual_type):
                            self.errors.append(TypeCheckError(
                                message=f"Function expects return type '{expected_type}' but got '{actual_type}'",
                                suggestion=f"Return a value of type '{expected_type}' or convert the current value",
                                position=node["value"]["position"]
                            ))
            
        elif node_type == "block":
            self.symbol_table.enter_scope("block")
            
            for stmt in node.get("statements", []):
                self._check_node(stmt)
                
            self.symbol_table.exit_scope()
            
        elif node_type == "identifier":
            name = node["name"]
            symbol = self.symbol_table.lookup(name)
            
            if not symbol:
                self.errors.append(TypeCheckError(
                    message=f"Undefined symbol '{name}'",
                    suggestion=f"Declare the variable before using it or check for typos",
                    position=node["position"]
                ))
                return None
                
            if symbol.symbol_type == SymbolType.VARIABLE:
                return symbol.type_info
            elif symbol.symbol_type == SymbolType.FUNCTION:
                return "function"
            elif symbol.symbol_type == SymbolType.TYPE:
                return "type"
            
            return None
            
        elif node_type == "member_access":
            object_type = self._check_node(node["object"])
            member_name = node["member"]
            
            # Get the field type from the struct or enum
            field_type = self._get_member_type(object_type, member_name, node["position"])
            return field_type
            
        elif node_type == "literal":
            literal_type = node.get("literal_type", "")
            
            if literal_type == "int":
                return "int"
            elif literal_type == "float":
                return "float"
            elif literal_type == "bool":
                return "bool"
            elif literal_type == "string":
                return "string"
            else:
                return None
                
        elif node_type == "match_statement":
            subject_type = self._check_node(node["subject"])
            
            # Check each branch
            for branch in node.get("branches", []):
                self.symbol_table.enter_scope("match_branch")
                
                # Check pattern compatibility with subject
                pattern = branch["pattern"]
                if pattern.get("node_type") == "identifier":
                    # Binding pattern - adds variable to scope
                    self.symbol_table.add_symbol(
                        name=pattern["name"],
                        symbol_type=SymbolType.VARIABLE,
                        type_info=subject_type or "any"
                    )
                elif subject_type:
                    # Check if pattern is compatible with subject type
                    self._check_match_pattern(subject_type, pattern)
                
                # Check guard condition
                if branch.get("guard"):
                    guard_type = self._check_node(branch["guard"])
                    if guard_type and guard_type != "bool":
                        self.errors.append(TypeCheckError(
                            message=f"Match guard must be a boolean, got '{guard_type}'",
                            suggestion="Use a comparison or logical expression that evaluates to a boolean",
                            position=branch["guard"]["position"]
                        ))
                
                # Check branch body
                self._check_node(branch["body"])
                
                self.symbol_table.exit_scope()
                
        elif node_type == "await_expression":
            expression_type = self._check_node(node["expression"])
            
            # Check if we're in an async function
            if self.current_function and not self.current_function.get("is_async", False):
                self.errors.append(TypeCheckError(
                    message="Cannot use 'await' outside of an async function",
                    suggestion="Mark the enclosing function as async using the 'async' keyword",
                    position=node["position"]
                ))
            
            # Check if expression is awaitable
            awaitable_type = self._get_awaitable_type(expression_type, node["position"])
            return awaitable_type
            
        elif node_type == "task_spawn":
            # Check task body
            self.symbol_table.enter_scope("task")
            body_type = self._check_node(node["body"])
            self.symbol_table.exit_scope()
            
            # Task types always wrap their result type
            return f"Task<{body_type or 'void'}>"
        
        return None
    
    def _is_valid_type(self, type_name: str) -> bool:
        """Check if a type name refers to a valid type."""
        # Primitive types
        if type_name in ["int", "float", "bool", "string", "void", "any"]:
            return True
            
        # Check user-defined types
        symbol = self.symbol_table.lookup(type_name)
        return symbol is not None and symbol.symbol_type == SymbolType.TYPE
    
    def _are_types_compatible(self, target_type: str, source_type: str) -> bool:
        """Check if source_type can be assigned to target_type."""
        # Same types are always compatible
        if target_type == source_type:
            return True
            
        # Any can be assigned to any type (dynamic escape hatch)
        if source_type == "any" or target_type == "any":
            return True
            
        # Numeric conversions with potential precision loss are not allowed
        # (would require explicit casts)
        if target_type == "int" and source_type == "float":
            return False
            
        # Float can accept int (widening conversion)
        if target_type == "float" and source_type == "int":
            return True
            
        # Generic type compatibility
        if "<" in target_type and "<" in source_type:
            # Extract the base types and type parameters
            target_base = target_type.split("<")[0]
            source_base = source_type.split("<")[0]
            
            if target_base != source_base:
                return False
                
            # Extract and check type parameters
            target_params = target_type[target_type.index("<")+1:target_type.rindex(">")].split(",")
            source_params = source_type[source_type.index("<")+1:source_type.rindex(">")].split(",")
            
            if len(target_params) != len(source_params):
                return False
                
            for i in range(len(target_params)):
                if not self._are_types_compatible(target_params[i].strip(), source_params[i].strip()):
                    return False
                    
            return True
            
        # For user-defined types, check hierarchy (would need trait/impl info)
        # Placeholder for future trait/inheritance compatibility
        
        return False
    
    def _check_binary_op_types(self, left_type: str, right_type: str, operator: str, position: SourcePosition) -> Optional[str]:
        """Check if the binary operator can be applied to the given types."""
        # Handle arithmetic operators
        if operator in ["+", "-", "*", "/", "%"]:
            if left_type in ["int", "float"] and right_type in ["int", "float"]:
                # For mixed numeric operations, result is widest type
                if left_type == "float" or right_type == "float":
                    return "float"
                else:
                    return "int"
            elif operator == "+" and left_type == "string" and right_type == "string":
                # String concatenation
                return "string"
            else:
                self.errors.append(TypeCheckError(
                    message=f"Operator '{operator}' cannot be applied to types '{left_type}' and '{right_type}'",
                    suggestion=f"Use numeric types for arithmetic operations or strings for concatenation (+)",
                    position=position
                ))
                return None
                
        # Handle comparison operators
        elif operator in ["==", "!=", "<", ">", "<=", ">="]:
            if left_type is None or right_type is None:
                return None
                
            if left_type == right_type:
                # Same types can always be compared for equality
                return "bool"
            elif left_type in ["int", "float"] and right_type in ["int", "float"]:
                # Mixed numeric comparisons are valid
                return "bool"
            else:
                if operator in ["==", "!="]:
                    # Only allow equality checks if types are compatible
                    if self._are_types_compatible(left_type, right_type) or self._are_types_compatible(right_type, left_type):
                        return "bool"
                        
                self.errors.append(TypeCheckError(
                    message=f"Cannot compare values of types '{left_type}' and '{right_type}' with operator '{operator}'",
                    suggestion="Use comparable types or implement comparison operators for custom types",
                    position=position
                ))
                return None
                
        # Handle logical operators
        elif operator in ["&&", "||"]:
            if left_type == "bool" and right_type == "bool":
                return "bool"
            else:
                self.errors.append(TypeCheckError(
                    message=f"Logical operator '{operator}' requires boolean operands, got '{left_type}' and '{right_type}'",
                    suggestion="Use boolean expressions for logical operations",
                    position=position
                ))
                return None
        
        return None
    
    def _check_unary_op_types(self, operand_type: str, operator: str, position: SourcePosition) -> Optional[str]:
        """Check if the unary operator can be applied to the given type."""
        if operator == "-":
            if operand_type in ["int", "float"]:
                return operand_type
            else:
                self.errors.append(TypeCheckError(
                    message=f"Unary minus operator cannot be applied to type '{operand_type}'",
                    suggestion="Use a numeric type with the negation operator",
                    position=position
                ))
                return None
                
        elif operator == "!":
            if operand_type == "bool":
                return "bool"
            else:
                self.errors.append(TypeCheckError(
                    message=f"Logical not operator cannot be applied to type '{operand_type}'",
                    suggestion="Use a boolean value or expression with the logical not operator",
                    position=position
                ))
                return None
        
        return None
    
    def _check_function_call(self, func_name: str, args: List[Dict[str, Any]], position: SourcePosition) -> Optional[str]:
        """Check function call for correct argument types and return the return type."""
        symbol = self.symbol_table.lookup(func_name)
        
        if not symbol or symbol.symbol_type != SymbolType.FUNCTION:
            self.errors.append(TypeCheckError(
                message=f"Call to undefined function '{func_name}'",
                suggestion="Define the function before calling it or check for typos",
                position=position
            ))
            return None
            
        # Check argument count
        params = symbol.type_info["params"]
        if len(args) != len(params):
            self.errors.append(TypeCheckError(
                message=f"Function '{func_name}' expects {len(params)} arguments but got {len(args)}",
                suggestion=f"Provide exactly {len(params)} arguments as defined in the function signature",
                position=position
            ))
            return None
            
        # Check argument types
        for i, arg in enumerate(args):
            arg_type = self._check_node(arg)
            param_name, param_type = params[i]
            
            if arg_type and param_type and not self._are_types_compatible(param_type, arg_type):
                self.errors.append(TypeCheckError(
                    message=f"Function '{func_name}' expects parameter '{param_name}' of type '{param_type}' but got '{arg_type}'",
                    suggestion=f"Provide a value of type '{param_type}' or convert the argument to that type",
                    position=arg["position"]
                ))
        
        return symbol.type_info["return_type"]
    
    def _check_method_call(self, member_access: Dict[str, Any], args: List[Dict[str, Any]], position: SourcePosition) -> Optional[str]:
        """Check method call for correct argument types and return the return type."""
        object_type = self._check_node(member_access["object"])
        method_name = member_access["member"]
        
        if not object_type:
            return None
            
        # Find the method in the type definition
        method_info = self._get_method_info(object_type, method_name)
        
        if not method_info:
            self.errors.append(TypeCheckError(
                message=f"Type '{object_type}' has no method named '{method_name}'",
                suggestion=f"Check for typos or implement the method for type '{object_type}'",
                position=position
            ))
            return None
            
        # Check argument count (accounting for implicit self)
        params = method_info["params"]
        expected_arg_count = len(params) - 1  # Subtract 1 for implicit self
        
        if len(args) != expected_arg_count:
            self.errors.append(TypeCheckError(
                message=f"Method '{method_name}' expects {expected_arg_count} arguments but got {len(args)}",
                suggestion=f"Provide exactly {expected_arg_count} arguments as defined in the method signature",
                position=position
            ))
            return None
            
        # Check argument types (starting from index 1 to skip self)
        for i, arg in enumerate(args):
            arg_type = self._check_node(arg)
            _, param_type = params[i + 1]  # +1 to skip self
            
            if arg_type and param_type and not self._are_types_compatible(param_type, arg_type):
                self.errors.append(TypeCheckError(
                    message=f"Method '{method_name}' expects argument of type '{param_type}' but got '{arg_type}'",
                    suggestion=f"Provide a value of type '{param_type}' or convert the argument to that type",
                    position=arg["position"]
                ))
        
        return method_info["return_type"]
    
    def _get_member_type(self, object_type: str, member_name: str, position: SourcePosition) -> Optional[str]:
        """Get the type of a member (field or method) of a struct or enum."""
        if not object_type:
            return None
            
        # Look up the type
        symbol = self.symbol_table.lookup(object_type)
        
        if not symbol or symbol.symbol_type != SymbolType.TYPE:
            self.errors.append(TypeCheckError(
                message=f"Cannot access member '{member_name}' on non-struct/enum type '{object_type}'",
                suggestion="Use a struct or enum type with the member access operator",
                position=position
            ))
            return None
            
        type_info = symbol.type_info
        kind = type_info.get("kind", "")
        
        if kind == "struct":
            # Check struct fields
            fields = type_info.get("fields", {})
            if member_name in fields:
                return fields[member_name]
                
            # Could be a method, which would be handled by the call node
            
        elif kind == "enum":
            # For enums, members are typically methods, handled by the call node
            pass
            
        self.errors.append(TypeCheckError(
            message=f"Type '{object_type}' has no member named '{member_name}'",
            suggestion=f"Check for typos or add the member to type '{object_type}'",
            position=position
        ))
        
        return None
    
    def _get_method_info(self, object_type: str, method_name: str) -> Optional[Dict[str, Any]]:
        """Get information about a method of a struct, enum, or trait."""
        # Look up the type
        symbol = self.symbol_table.lookup(object_type)
        
        if not symbol or symbol.symbol_type != SymbolType.TYPE:
            return None
            
        type_info = symbol.type_info
        
        # Find method implementation
        # For now, methods are not properly modeled in our prototype
        # This would require tracking method implementations for types
        
        # Simple placeholder for demo purposes
        # In a real implementation, we'd look through the type's methods and trait implementations
        return {
            "params": [("self", object_type)],  # Self parameter
            "return_type": "any"  # Placeholder
        }
    
    def _get_element_type(self, collection_type: str) -> Optional[str]:
        """Get the element type of a collection."""
        if not collection_type:
            return None
            
        # Array types
        if collection_type.startswith("Array<") and collection_type.endswith(">"):
            element_type = collection_type[6:-1]  # Extract type parameter
            return element_type
            
        # Range type
        if collection_type == "Range":
            return "int"
            
        # String type (iterates characters)
        if collection_type == "string":
            return "char"
            
        # Other iterable types would need more sophisticated analysis
        
        return None
    
    def _get_awaitable_type(self, awaitable_type: str, position: SourcePosition) -> Optional[str]:
        """Get the result type of an awaitable expression."""
        if not awaitable_type:
            return None
            
        # Task and Future types
        if awaitable_type.startswith("Task<") and awaitable_type.endswith(">"):
            result_type = awaitable_type[5:-1]  # Extract type parameter
            return result_type
            
        if awaitable_type.startswith("Future<") and awaitable_type.endswith(">"):
            result_type = awaitable_type[7:-1]  # Extract type parameter
            return result_type
            
        # Not an awaitable type
        self.errors.append(TypeCheckError(
            message=f"Type '{awaitable_type}' is not awaitable",
            suggestion="Use a Task<T> or Future<T> type that can be awaited in an async function",
            position=position
        ))
        return None
    
    def _check_match_pattern(self, subject_type: str, pattern: Dict[str, Any]) -> None:
        """
        Check if a match pattern is compatible with the subject type.
        
        Args:
            subject_type: The type of the match subject
            pattern: The pattern AST node
        """
        if pattern.get("node_type") == "identifier":
            # This is a binding pattern, already handled
            return
            
        # For enum variant patterns
        if pattern.get("node_type") == "variant_pattern":
            variant_name = pattern.get("name", "")
            
            # Check if subject is an enum
            symbol = self.symbol_table.lookup(subject_type)
            if not symbol or symbol.symbol_type != SymbolType.TYPE:
                self.errors.append(TypeCheckError(
                    message=f"Cannot match non-enum type '{subject_type}' against variant pattern",
                    suggestion=f"Use a simple binding pattern or ensure the matched value is an enum",
                    position=pattern["position"]
                ))
                return
                
            type_info = symbol.type_info
            if type_info.get("kind") != "enum":
                self.errors.append(TypeCheckError(
                    message=f"Cannot match non-enum type '{subject_type}' against variant pattern",
                    suggestion=f"Use a simple binding pattern or ensure the matched value is an enum",
                    position=pattern["position"]
                ))
                return
                
            # Check if variant exists
            variants = type_info.get("variants", {})
            if variant_name not in variants:
                self.errors.append(TypeCheckError(
                    message=f"Enum '{subject_type}' has no variant named '{variant_name}'",
                    suggestion=f"Use one of the defined variants: {', '.join(variants.keys())}",
                    position=pattern["position"]
                ))
                return
                
            # Check pattern arguments match variant fields
            variant_fields = variants[variant_name]
            pattern_fields = pattern.get("fields", [])
            
            if len(pattern_fields) != len(variant_fields):
                self.errors.append(TypeCheckError(
                    message=f"Variant '{variant_name}' expects {len(variant_fields)} fields but got {len(pattern_fields)}",
                    suggestion=f"Provide the correct number of fields for this variant",
                    position=pattern["position"]
                ))
                
            # More detailed field checking could be added here
                
        # Literal patterns
        elif pattern.get("node_type") == "literal":
            literal_type = pattern.get("literal_type", "")
            
            if not self._are_types_compatible(subject_type, literal_type):
                self.errors.append(TypeCheckError(
                    message=f"Cannot match value of type '{subject_type}' against literal of type '{literal_type}'",
                    suggestion=f"Use a pattern of type '{subject_type}'",
                    position=pattern["position"]
                ))
    
    def check_match_exhaustiveness(self, subject_type: str, branches: List[Dict[str, Any]], position: SourcePosition) -> None:
        """
        Check if a match statement covers all possible variants of an enum.
        
        Args:
            subject_type: The type being matched on
            branches: The match branches
            position: The source position of the match statement
        """
        # Only check exhaustiveness for enum types
        symbol = self.symbol_table.lookup(subject_type)
        if not symbol or symbol.symbol_type != SymbolType.TYPE:
            return
            
        type_info = symbol.type_info
        if type_info.get("kind") != "enum":
            return
            
        # Get all variants for this enum
        all_variants = set(type_info.get("variants", {}).keys())
        covered_variants = set()
        has_wildcard = False
        
        # Check which variants are covered
        for branch in branches:
            pattern = branch.get("pattern", {})
            
            if pattern.get("node_type") == "identifier":
                # This is a catch-all binding pattern
                has_wildcard = True
                break
                
            elif pattern.get("node_type") == "variant_pattern":
                variant_name = pattern.get("name", "")
                covered_variants.add(variant_name)
        
        # If we have a wildcard pattern, all variants are covered
        if has_wildcard:
            return
            
        # Check if all variants are covered
        missing_variants = all_variants - covered_variants
        if missing_variants:
            self.errors.append(TypeCheckError(
                message=f"Match statement for enum '{subject_type}' is not exhaustive, missing variants: {', '.join(missing_variants)}",
                suggestion="Add patterns for all variants or include a catch-all pattern with '_'",
                position=position
            ))