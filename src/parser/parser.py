from src.lexer.lexer import lex
from utils.logger import get_logger

logger = get_logger(__name__)
# -------------------------------
# Parser Implementation
# -------------------------------
# A TokenStream class to manage tokens.
# An ASTNode class to build the abstract syntax tree.
# An AegisParser that produces the AST from tokens.
class TokenStream:
    """A simple stream to process tokens sequentially."""
    def __init__(self, tokens):
        logger.info("Starting TokenStream...")
        self.tokens = tokens
        self.index = 0

    def peek(self):
        """Returns the current token without consuming it."""
        logger.debug(f"Peeking token: {self.tokens[self.index]}")
        if self.index < len(self.tokens):
            return self.tokens[self.index]
        logger.warning("No more tokens to peek.")
        return None

    def consume(self):
        """Consumes the current token and moves to the next."""
        logger.info("Consuming token...")
        token = self.peek()
        self.index += 1
        logger.debug(f"Consumed token: {token}")
        return token

    def expect(self, expected_type):
        """Consumes and verifies a token type."""
        logger.info("Expecting token...")
        token = self.consume()
        if token is None or token[0] != expected_type:
            raise SyntaxError(f"Expected {expected_type}, but got {token}")
        logger.debug(f"Expected token: {token}")
        return token


class ASTNode:
    """Base class for AST nodes."""
    def __init__(self, node_type, value=None):
        logger.info("Initializing ASTNode...")
        self.node_type = node_type
        self.value = value
        self.children = []
    def add_child(self, child):
        self.children.append(child)
    def __repr__(self):
        logger.debug(f"ASTNode: {self.node_type}({self.value}, children={self.children})")
        return f"{self.node_type}({self.value}, children={self.children})"


class AegisParser:
    """Enhanced parser with improved error handling."""
    def __init__(self, tokens):
        logger.info("Initializing AegisParser...")
        self.tokens = TokenStream(tokens)

    def parse_module(self):
        """Parses a module declaration."""
        logger.info("Parsing module...")
        self.tokens.expect("KEYWORD")  # "module"
        module_name = self.tokens.expect("IDENTIFIER")[1]
        self.tokens.expect("SYMBOL")  # ":" correctly defined as SYMBOL
        module_node = ASTNode("Module", module_name)
        logger.debug(f"Module parsed with name: {module_name}")

        # parse children
        while self.tokens.peek() and self.tokens.peek()[0] == "KEYWORD":
            keyword = self.tokens.peek()[1]
            if keyword == "struct":
                module_node.add_child(self.parse_struct())
            elif keyword == "fn":
                module_node.add_child(self.parse_function())
            else:
                break
        logger.debug(f"Parsed module: {module_node}")
        return module_node

    def parse_struct(self):
        """Parses a struct declaration."""  
        logger.info("Parsing struct...")
        self.tokens.expect("KEYWORD")  # "struct"
        struct_name = self.tokens.expect("IDENTIFIER")[1]
        self.tokens.expect("OPERATOR")  # ":"
        struct_node = ASTNode("Struct", struct_name)

        # parse fields
        while self.tokens.peek() and self.tokens.peek()[0] == "IDENTIFIER":
            field_name = self.tokens.expect("IDENTIFIER")[1]
            self.tokens.expect("OPERATOR")  # ":"
            field_type = self.tokens.expect("TYPE")[1]
            struct_node.add_child(ASTNode("Field", (field_name, field_type)))
        logger.debug(f"Parsed struct: {struct_node}")
        return struct_node

    def parse_function(self):
        """Parses a function declaration."""
        logger.info("Parsing function...")
        """fn <Name>(<Params>) -> <ReturnType>"""
        self.tokens.expect("KEYWORD")  # "fn"
        function_name = self.tokens.expect("IDENTIFIER")[1]
        self.tokens.expect("SYMBOL")  # "("
        params = []
        # parse params
        while self.tokens.peek() and self.tokens.peek()[0] == "IDENTIFIER":
            param_name = self.tokens.expect("IDENTIFIER")[1]
            self.tokens.expect("OPERATOR")  # ":"
            token = self.tokens.peek()
            if token[0] == "TYPE":
                param_type = self.tokens.expect("TYPE")[1]
            else:
                # user-defined type
                param_type = self.tokens.expect("IDENTIFIER")[1]
            params.append((param_name, param_type))
            if self.tokens.peek() and self.tokens.peek()[0] == "SYMBOL":
                if self.tokens.peek()[1] == ")":
                    break
                self.tokens.expect("SYMBOL")  # ","
        self.tokens.expect("SYMBOL")  # ")"
        self.tokens.expect("OPERATOR")  # "->"
        # Allow both built-in types and user-defined types
        token = self.tokens.peek()
        if token[0] == "TYPE":
            return_type = self.tokens.expect("TYPE")[1]
        else:
            return_type = self.tokens.expect("IDENTIFIER")[1]
        self.tokens.expect("OPERATOR")  # ":"
        func_node = ASTNode("Function", function_name)
        func_node.add_child(ASTNode("Parameters", params))
        func_node.add_child(ASTNode("ReturnType", return_type))
        logger.debug(f"Parsed function: {func_node}")
        return func_node

    def parse_block(self):
        """Parse an indentation-based block."""
        logger.info("Parsing block...")
        self.tokens.expect("INDENT", context="block")
        block_nodes = []
        while self.tokens.peek() and self.tokens.peek()[0] != "DEDENT":
            # Parse statements in the block
            if self.tokens.peek()[0] == "KEYWORD":
                keyword = self.tokens.peek()[1]
                if keyword == "if":
                    block_nodes.append(self.parse_if_statement())
                elif keyword == "while":
                    block_nodes.append(self.parse_while_statement())
                elif keyword == "return":
                    block_nodes.append(self.parse_return_statement())
                # Add other statement types as needed
            elif self.tokens.peek()[0] == "IDENTIFIER":
                block_nodes.append(self.parse_expression_statement())

            # Expect a newline after each statement
            self.tokens.expect("NEWLINE", context="statement")
        self.tokens.expect("DEDENT", context="end of block")
        logger.debug(f"Parsed block: {block_nodes}")
        return block_nodes

    def parse_if_statement(self):
        logger.warning("parse_if_statement not implemented yet.")
        pass  # TODO: implement

    def parse_while_statement(self):
        logger.warning("parse_while_statement not implemented yet.")
        pass  # TODO: implement

    def parse_return_statement(self):
        logger.warning("parse_return_statement not implemented yet.")
        pass  # TODO: implement

    def parse(self):
        """Parses the entire code into an AST."""
        logger.info("Parsing entire code...")
        return self.parse_module()

    def expect(self, expected_type, context=None):
        """Expects a token of a specific type with improved error messages."""
        logger.info("Expecting token...")
        token = self.tokens.consume()
        if token is None:
            context_msg = f" while parsing {context}" if context else ""
            raise SyntaxError(
                f"Unexpected end of file{context_msg}. Expected {expected_type}."
            )

        if token[0] != expected_type:
            line = token[2] if len(token) > 2 else "unknown"
            column = token[3] if len(token) > 3 else "unknown"
            context_msg = f" while parsing {context}" if context else ""

            raise SyntaxError(
                f"Line {line}, column {column}{context_msg}: "
                f"Expected {expected_type}, but got {token[0]} ('{token[1]}')"
            )
        logger.debug(f"Expected token: {token}")
        return token
