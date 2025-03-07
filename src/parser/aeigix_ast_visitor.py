"""
AegisASTVisitor - Abstract Syntax Tree Visitor for Aegis programming language.

This visitor traverses the AST produced by the parser and creates a structured 
representation that can be used for semantic analysis, IR generation, and code
optimization. Each method corresponds to a specific node type in the Aegis language.

The visitor pattern makes it easy to analyze and transform the AST in an organized,
maintainable way while preserving the language's strict typing and deterministic 
execution model.
"""

from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

@dataclass
class SourcePosition:
    """Represents a position in the source code file"""
    line: int
    column: int
    file_path: str = ""

    def __str__(self) -> str:
        return f"{self.file_path}:{self.line}:{self.column}"

class AegisASTVisitor:
    """
    Visitor for traversing Aegis language Abstract Syntax Trees.
    
    This visitor implements methods for all language constructs in Aegis,
    creating a structured representation that preserves the semantic meaning
    while making it suitable for AI-driven analysis and transformation.
    """
    
    def __init__(self, source_file: str = ""):
        """
        Initialize the AST visitor.
        
        Args:
            source_file: Path to the source file being processed
        """
        self.source_file = source_file
        self.current_module = None
        self.errors = []
        
    def _make_node_info(self, node_type: str, name: str, 
                       children: List[Any], pos: SourcePosition,
                       **extra_info) -> Dict[str, Any]:
        """Helper method to create consistent node information dictionaries."""
        info = {
            "node_type": node_type,
            "name": name,
            "children": children,
            "position": pos,
        }
        # Add any extra info specific to the node type
        info.update(extra_info)
        return info
    
    def visit_module(self, node) -> Dict[str, Any]:
        """
        Visit a module declaration node.
        
        In Aegis, modules are top-level containers that group related functionality.
        They provide namespace isolation and encapsulation.
        
        Constraints:
        - Module names must be unique within a project
        - Modules can contain structs, enums, functions, and other declarations
        - Modules can be nested but must follow a logical hierarchy
        
        Example in Aegis:
            module Math:
                fn add(a: int, b: int) -> int:
                    return a + b
        
        Returns:
            Dictionary with module information
        """
        logger.debug(f"Visiting module: {node.name}")
        
        old_module = self.current_module
        self.current_module = node.name
        
        # Recursively visit all children
        children = []
        for item in node.body:
            children.append(self.visit(item))
            
        self.current_module = old_module
        
        return self._make_node_info(
            node_type="module",
            name=node.name,
            children=children,
            pos=SourcePosition(node.line, node.column, self.source_file),
            exports=node.exports if hasattr(node, "exports") else []
        )
    
    def visit_struct(self, node) -> Dict[str, Any]:
        """
        Visit a struct declaration node.
        
        In Aegis, structs are strongly-typed composite data structures.
        They have named fields with specific types and no nullable fields.
        
        Constraints:
        - Field names must be unique within a struct
        - All fields must have explicit type annotations
        - No implicit type conversions or nullable fields without Option<T>
        - Structs can implement traits and have methods
        
        Example in Aegis:
            struct Point:
                x: float
                y: float
                
                fn distance(self, other: Point) -> float:
                    # Function body
        
        Returns:
            Dictionary with struct information
        """
        logger.debug(f"Visiting struct: {node.name}")
        
        fields = []
        methods = []
        
        for item in node.body:
            if hasattr(item, "type") and item.type == "field":
                fields.append(self.visit_field(item))
            elif hasattr(item, "type") and item.type == "function":
                methods.append(self.visit_function(item))
        
        return self._make_node_info(
            node_type="struct",
            name=node.name,
            children=fields + methods,
            pos=SourcePosition(node.line, node.column, self.source_file),
            fields=fields,
            methods=methods,
            traits=node.traits if hasattr(node, "traits") else []
        )
    
    def visit_enum(self, node) -> Dict[str, Any]:
        """
        Visit an enum declaration node.
        
        In Aegis, enums represent a type that can be one of several variants.
        Each variant can optionally contain data. Enums are used for 
        pattern matching and representing states.
        
        Constraints:
        - Variant names must be unique within an enum
        - Variants can contain typed data fields
        - Enums can have methods
        - Enum variants must be exhaustively matched in pattern matching
        
        Example in Aegis:
            enum Result<T, E>:
                Ok(T)
                Err(E)
                
                fn is_ok(self) -> bool:
                    # Function body
        
        Returns:
            Dictionary with enum information
        """
        logger.debug(f"Visiting enum: {node.name}")
        
        variants = []
        methods = []
        
        for item in node.body:
            if hasattr(item, "type") and item.type == "variant":
                variants.append(self.visit_variant(item))
            elif hasattr(item, "type") and item.type == "function":
                methods.append(self.visit_function(item))
        
        return self._make_node_info(
            node_type="enum",
            name=node.name,
            children=variants + methods,
            pos=SourcePosition(node.line, node.column, self.source_file),
            variants=variants,
            methods=methods,
            type_params=node.type_params if hasattr(node, "type_params") else []
        )
    
    def visit_variant(self, node) -> Dict[str, Any]:
        """
        Visit an enum variant node.
        
        Enum variants can be simple identifiers or can contain data.
        
        Example in Aegis:
            enum Option<T>:
                Some(T)  # variant with data
                None     # simple variant
        
        Returns:
            Dictionary with variant information
        """
        fields = []
        
        if hasattr(node, "fields") and node.fields:
            for field in node.fields:
                fields.append(self.visit_field(field))
        
        return self._make_node_info(
            node_type="variant",
            name=node.name,
            children=fields,
            pos=SourcePosition(node.line, node.column, self.source_file),
            fields=fields
        )
    
    def visit_field(self, node) -> Dict[str, Any]:
        """
        Visit a field declaration node (in structs or enum variants).
        
        Fields in Aegis have a name and an explicit type annotation.
        There are no implicit types or nullable fields.
        
        Example in Aegis:
            struct User:
                name: string
                age: int
        
        Returns:
            Dictionary with field information
        """
        type_info = self.visit_type(node.type_annotation)
        
        return self._make_node_info(
            node_type="field",
            name=node.name,
            children=[type_info],
            pos=SourcePosition(node.line, node.column, self.source_file),
            type_annotation=type_info,
            default_value=self.visit(node.default_value) if hasattr(node, "default_value") and node.default_value else None
        )
    
    def visit_function(self, node) -> Dict[str, Any]:
        """
        Visit a function declaration node.
        
        Functions in Aegis have explicit parameter types and return types.
        They can be regular functions, methods (with 'self' parameter),
        or async functions.
        
        Constraints:
        - All parameters must have explicit type annotations
        - Return type must be explicit
        - Async functions must be marked with 'async' keyword
        - Methods in structs/enums have implicit 'self' parameter
        
        Example in Aegis:
            fn add(a: int, b: int) -> int:
                return a + b
                
            async fn fetch_data(url: string) -> Result<string, Error>:
                # Function body
        
        Returns:
            Dictionary with function information
        """
        logger.debug(f"Visiting function: {node.name}")
        
        params = []
        for param in node.params:
            params.append(self.visit_parameter(param))
        
        return_type = self.visit_type(node.return_type) if hasattr(node, "return_type") and node.return_type else None
        
        body_nodes = []
        for stmt in node.body:
            body_nodes.append(self.visit(stmt))
        
        return self._make_node_info(
            node_type="function",
            name=node.name,
            children=params + (body_nodes if body_nodes else []),
            pos=SourcePosition(node.line, node.column, self.source_file),
            params=params,
            return_type=return_type,
            body=body_nodes,
            is_async=node.is_async if hasattr(node, "is_async") else False,
            is_method=node.is_method if hasattr(node, "is_method") else False,
            visibility=node.visibility if hasattr(node, "visibility") else "public"
        )
    
    def visit_parameter(self, node) -> Dict[str, Any]:
        """
        Visit a function parameter node.
        
        Parameters in Aegis have a name and an explicit type annotation.
        
        Example in Aegis:
            fn greet(name: string, age: int) -> string:
                # Function body
        
        Returns:
            Dictionary with parameter information
        """
        type_info = self.visit_type(node.type_annotation)
        
        return self._make_node_info(
            node_type="parameter",
            name=node.name,
            children=[type_info],
            pos=SourcePosition(node.line, node.column, self.source_file),
            type_annotation=type_info,
            default_value=self.visit(node.default_value) if hasattr(node, "default_value") and node.default_value else None
        )
    
    def visit_type(self, node) -> Dict[str, Any]:
        """
        Visit a type annotation node.
        
        Type annotations in Aegis can be primitive types, user-defined types,
        or generic types with type parameters.
        
        Examples of Aegis types:
            int
            string
            User
            Option<int>
            Result<User, Error>
            fn(int, string) -> bool  # Function type
        
        Returns:
            Dictionary with type information
        """
        if node is None:
            return None
        
        type_params = []
        if hasattr(node, "type_params") and node.type_params:
            for param in node.type_params:
                type_params.append(self.visit_type(param))
        
        return self._make_node_info(
            node_type="type",
            name=node.name,
            children=type_params,
            pos=SourcePosition(node.line, node.column, self.source_file),
            is_primitive=node.is_primitive if hasattr(node, "is_primitive") else False,
            type_params=type_params
        )
    
    def visit_block(self, node) -> Dict[str, Any]:
        """
        Visit a block node.
        
        Blocks in Aegis are sequences of statements, potentially with their own scope.
        
        Example in Aegis:
            fn example():
                # This is a block
                let x: int = 1
                let y: int = 2
                return x + y
        
        Returns:
            Dictionary with block information
        """
        statements = []
        
        for stmt in node.statements:
            statements.append(self.visit(stmt))
        
        return self._make_node_info(
            node_type="block",
            name="",
            children=statements,
            pos=SourcePosition(node.line, node.column, self.source_file),
            statements=statements
        )
    
    def visit_var_declaration(self, node) -> Dict[str, Any]:
        """
        Visit a variable declaration node.
        
        Variables in Aegis must have explicit type annotations and can be
        mutable (var) or immutable (let).
        
        Constraints:
        - All variables must have explicit type annotations
        - Variables can be immutable (let) or mutable (var)
        - Immutable variables cannot be reassigned
        
        Example in Aegis:
            let x: int = 5  # immutable
            var y: int = 10  # mutable
        
        Returns:
            Dictionary with variable declaration information
        """
        type_info = self.visit_type(node.type_annotation)
        init_value = self.visit(node.value) if hasattr(node, "value") and node.value else None
        
        return self._make_node_info(
            node_type="var_declaration",
            name=node.name,
            children=[type_info] + ([init_value] if init_value else []),
            pos=SourcePosition(node.line, node.column, self.source_file),
            is_mutable=node.is_mutable,
            type_annotation=type_info,
            init_value=init_value
        )
    
    def visit_assignment(self, node) -> Dict[str, Any]:
        """
        Visit an assignment node.
        
        Assignments in Aegis update the value of a mutable variable or a field.
        
        Constraints:
        - The target must be a mutable variable or field
        - The assigned value must match the target's type
        - No implicit type conversions
        
        Example in Aegis:
            var x: int = 5
            x = 10  # assignment
            user.name = "Alice"  # field assignment
        
        Returns:
            Dictionary with assignment information
        """
        target = self.visit(node.target)
        value = self.visit(node.value)
        
        return self._make_node_info(
            node_type="assignment",
            name="",
            children=[target, value],
            pos=SourcePosition(node.line, node.column, self.source_file),
            target=target,
            value=value,
            operator=node.operator if hasattr(node, "operator") else "="
        )
    
    def visit_if_statement(self, node) -> Dict[str, Any]:
        """
        Visit an if statement node.
        
        If statements in Aegis include a condition and one or more branches.
        
        Constraints:
        - The condition must evaluate to a boolean
        - Each branch has its own scope
        
        Example in Aegis:
            if x > 5:
                println("x is greater than 5")
            elif x > 0:
                println("x is positive but not greater than 5")
            else:
                println("x is not positive")
        
        Returns:
            Dictionary with if statement information
        """
        condition = self.visit(node.condition)
        then_block = self.visit(node.then_block)
        
        else_block = None
        if hasattr(node, "else_block") and node.else_block:
            else_block = self.visit(node.else_block)
        
        elif_branches = []
        if hasattr(node, "elif_branches") and node.elif_branches:
            for branch in node.elif_branches:
                elif_cond = self.visit(branch.condition)
                elif_block = self.visit(branch.block)
                elif_branches.append({"condition": elif_cond, "block": elif_block})
        
        return self._make_node_info(
            node_type="if_statement",
            name="",
            children=[condition, then_block] + ([else_block] if else_block else []),
            pos=SourcePosition(node.line, node.column, self.source_file),
            condition=condition,
            then_block=then_block,
            else_block=else_block,
            elif_branches=elif_branches
        )
    
    def visit_for_loop(self, node) -> Dict[str, Any]:
        """
        Visit a for loop node.
        
        For loops in Aegis iterate over collections or ranges.
        
        Constraints:
        - Iterator variable type is inferred from the collection
        - Collection must be iterable
        
        Example in Aegis:
            for i in 0..10:
                println(i)
                
            for item in items:
                process(item)
        
        Returns:
            Dictionary with for loop information
        """
        iterator = self.visit_var_declaration(node.iterator) if hasattr(node, "iterator_type") else self.visit(node.iterator)
        iterable = self.visit(node.iterable)
        body = self.visit(node.body)
        
        return self._make_node_info(
            node_type="for_loop",
            name="",
            children=[iterator, iterable, body],
            pos=SourcePosition(node.line, node.column, self.source_file),
            iterator=iterator,
            iterable=iterable,
            body=body
        )
    
    def visit_while_loop(self, node) -> Dict[str, Any]:
        """
        Visit a while loop node.
        
        While loops in Aegis execute a block as long as a condition is true.
        
        Constraints:
        - The condition must evaluate to a boolean
        
        Example in Aegis:
            while x > 0:
                x = x - 1
                println(x)
        
        Returns:
            Dictionary with while loop information
        """
        condition = self.visit(node.condition)
        body = self.visit(node.body)
        
        return self._make_node_info(
            node_type="while_loop",
            name="",
            children=[condition, body],
            pos=SourcePosition(node.line, node.column, self.source_file),
            condition=condition,
            body=body
        )
    
    def visit_return_statement(self, node) -> Dict[str, Any]:
        """
        Visit a return statement node.
        
        Return statements in Aegis specify the value to return from a function.
        
        Constraints:
        - The returned value must match the function's return type
        - A function with a non-void return type must return a value on all paths
        
        Example in Aegis:
            fn add(a: int, b: int) -> int:
                return a + b
        
        Returns:
            Dictionary with return statement information
        """
        value = self.visit(node.value) if hasattr(node, "value") and node.value else None
        
        return self._make_node_info(
            node_type="return_statement",
            name="",
            children=[value] if value else [],
            pos=SourcePosition(node.line, node.column, self.source_file),
            value=value
        )
    
    def visit_binary_op(self, node) -> Dict[str, Any]:
        """
        Visit a binary operation node.
        
        Binary operations in Aegis include arithmetic, comparison, and logical operations.
        
        Constraints:
        - Operands must be compatible with the operation
        - No implicit type conversions
        
        Example in Aegis:
            x + y
            a && b
            i < 10
        
        Returns:
            Dictionary with binary operation information
        """
        left = self.visit(node.left)
        right = self.visit(node.right)
        
        return self._make_node_info(
            node_type="binary_op",
            name=node.operator,
            children=[left, right],
            pos=SourcePosition(node.line, node.column, self.source_file),
            operator=node.operator,
            left=left,
            right=right
        )
    
    def visit_unary_op(self, node) -> Dict[str, Any]:
        """
        Visit a unary operation node.
        
        Unary operations in Aegis include negation, logical not, etc.
        
        Constraints:
        - Operand must be compatible with the operation
        
        Example in Aegis:
            -x
            !done
        
        Returns:
            Dictionary with unary operation information
        """
        operand = self.visit(node.operand)
        
        return self._make_node_info(
            node_type="unary_op",
            name=node.operator,
            children=[operand],
            pos=SourcePosition(node.line, node.column, self.source_file),
            operator=node.operator,
            operand=operand
        )
    
    def visit_call(self, node) -> Dict[str, Any]:
        """
        Visit a function call node.
        
        Function calls in Aegis invoke functions with arguments.
        
        Constraints:
        - The function must exist and be accessible
        - The arguments must match the function's parameter types
        - No implicit type conversions
        
        Example in Aegis:
            add(5, 10)
            user.get_name()
            println("Hello")
        
        Returns:
            Dictionary with function call information
        """
        callee = self.visit(node.callee)
        
        args = []
        for arg in node.args:
            args.append(self.visit(arg))
        
        return self._make_node_info(
            node_type="call",
            name="",
            children=[callee] + args,
            pos=SourcePosition(node.line, node.column, self.source_file),
            callee=callee,
            args=args
        )
    
    def visit_identifier(self, node) -> Dict[str, Any]:
        """
        Visit an identifier node.
        
        Identifiers in Aegis reference variables, functions, types, etc.
        
        Example in Aegis:
            x
            add
            User
        
        Returns:
            Dictionary with identifier information
        """
        return self._make_node_info(
            node_type="identifier",
            name=node.name,
            children=[],
            pos=SourcePosition(node.line, node.column, self.source_file)
        )
    
    def visit_member_access(self, node) -> Dict[str, Any]:
        """
        Visit a member access node.
        
        Member access in Aegis is used to access fields and methods of structs.
        
        Example in Aegis:
            user.name
            point.distance(other_point)
        
        Returns:
            Dictionary with member access information
        """
        object_expr = self.visit(node.object)
        
        return self._make_node_info(
            node_type="member_access",
            name=node.member,
            children=[object_expr],
            pos=SourcePosition(node.line, node.column, self.source_file),
            object=object_expr,
            member=node.member
        )
    
    def visit_literal(self, node) -> Dict[str, Any]:
        """
        Visit a literal value node.
        
        Literals in Aegis include numeric values, strings, booleans, etc.
        
        Examples in Aegis:
            42        # integer literal
            3.14      # float literal
            "hello"   # string literal
            true      # boolean literal
        
        Returns:
            Dictionary with literal information
        """
        return self._make_node_info(
            node_type="literal",
            name=str(node.value),
            children=[],
            pos=SourcePosition(node.line, node.column, self.source_file),
            value=node.value,
            literal_type=node.literal_type
        )
    
    def visit_match_statement(self, node) -> Dict[str, Any]:
        """
        Visit a match statement node.
        
        Match statements in Aegis provide pattern matching on values, particularly enums.
        
        Constraints:
        - Must be exhaustive (cover all possible cases)
        - Each branch has its own scope
        
        Example in Aegis:
            match result:
                Ok(value) => println("Success: {}", value)
                Err(e) => println("Error: {}", e)
        
        Returns:
            Dictionary with match statement information
        """
        subject = self.visit(node.subject)
        
        branches = []
        for branch in node.branches:
            pattern = self.visit(branch.pattern)
            body = self.visit(branch.body)
            
            branches.append({
                "pattern": pattern,
                "body": body,
                "guard": self.visit(branch.guard) if hasattr(branch, "guard") and branch.guard else None
            })
        
        return self._make_node_info(
            node_type="match_statement",
            name="",
            children=[subject],
            pos=SourcePosition(node.line, node.column, self.source_file),
            subject=subject,
            branches=branches
        )
    
    def visit_trait(self, node) -> Dict[str, Any]:
        """
        Visit a trait declaration node.
        
        Traits in Aegis define interfaces that types can implement.
        
        Constraints:
        - Trait names must be unique within a module
        - Traits can contain function signatures and default implementations
        
        Example in Aegis:
            trait Printable:
                fn to_string(self) -> string
                
                fn print(self):
                    println(self.to_string())
        
        Returns:
            Dictionary with trait information
        """
        methods = []
        
        for item in node.methods:
            methods.append(self.visit_function(item))
        
        return self._make_node_info(
            node_type="trait",
            name=node.name,
            children=methods,
            pos=SourcePosition(node.line, node.column, self.source_file),
            methods=methods,
            type_params=node.type_params if hasattr(node, "type_params") else []
        )
    
    def visit_impl(self, node) -> Dict[str, Any]:
        """
        Visit a trait implementation node.
        
        Impl blocks in Aegis implement traits for specific types.
        
        Constraints:
        - Must implement all methods required by the trait
        - Method signatures must match trait specifications
        
        Example in Aegis:
            impl Printable for User:
                fn to_string(self) -> string:
                    return "User {self.name}"
        
        Returns:
            Dictionary with implementation information
        """
        methods = []
        
        for item in node.methods:
            methods.append(self.visit_function(item))
        
        return self._make_node_info(
            node_type="impl",
            name="",
            children=methods,
            pos=SourcePosition(node.line, node.column, self.source_file),
            trait_name=node.trait_name if hasattr(node, "trait_name") else None,
            type_name=node.type_name,
            methods=methods
        )
    
    def visit_import(self, node) -> Dict[str, Any]:
        """
        Visit an import statement node.
        
        Import statements in Aegis bring modules, types, and functions into scope.
        
        Constraints:
        - Imported entities must exist
        - Imports can be selective or entire modules
        
        Example in Aegis:
            import Math
            import IO.{println, readln}
            import UserSystem.User as AppUser
        
        Returns:
            Dictionary with import statement information
        """
        return self._make_node_info(
            node_type="import",
            name=node.module_path,
            children=[],
            pos=SourcePosition(node.line, node.column, self.source_file),
            module_path=node.module_path,
            items=node.items if hasattr(node, "items") else [],
            alias=node.alias if hasattr(node, "alias") else None
        )
    
    def visit_async_await(self, node) -> Dict[str, Any]:
        """
        Visit an await expression node.
        
        Await expressions in Aegis are used inside async functions to wait for
        asynchronous operations to complete.
        
        Constraints:
        - Can only be used inside async functions
        - The awaited expression must be awaitable (Task or Future)
        
        Example in Aegis:
            async fn fetch_data() -> string:
                let response = await http.get("https://example.com")
                return response.body
        
        Returns:
            Dictionary with await expression information
        """
        expression = self.visit(node.expression)
        
        return self._make_node_info(
            node_type="await_expression",
            name="",
            children=[expression],
            pos=SourcePosition(node.line, node.column, self.source_file),
            expression=expression
        )
    
    def visit_task_spawn(self, node) -> Dict[str, Any]:
        """
        Visit a task spawn node.
        
        Task spawning in Aegis creates a new concurrent task.
        
        Example in Aegis:
            let t = task:
                heavy_computation()
            
            # later
            let result = await t
        
        Returns:
            Dictionary with task spawn information
        """
        body = self.visit(node.body)
        
        return self._make_node_info(
            node_type="task_spawn",
            name="",
            children=[body],
            pos=SourcePosition(node.line, node.column, self.source_file),
            body=body
        )
    
    def visit(self, node) -> Dict[str, Any]:
        """
        Generic visit method that dispatches to the appropriate specific visit method.
        
        Args:
            node: The AST node to visit
            
        Returns:
            Visited node information as a dictionary
        """
        if node is None:
            return None
        
        # Dispatch based on node type
        if hasattr(node, "type"):
            method_name = f"visit_{node.type}"
            if hasattr(self, method_name):
                return getattr(self, method_name)(node)
            else:
                logger.warning(f"No visitor method for node type: {node.type}")
                return {
                    "node_type": node.type,
                    "name": getattr(node, "name", ""),
                    "children": [],
                    "position": SourcePosition(
                        getattr(node, "line", 0),
                        getattr(node, "column", 0),
                        self.source_file
                    )
                }
        
        # Fallback for unknown node types
        logger.warning(f"Unknown node type: {type(node)}")
        return {
            "node_type": "unknown",
            "name": str(node),
            "children": [],
            "position": SourcePosition(0, 0, self.source_file)
        }
