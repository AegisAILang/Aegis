from antlr4 import Token
from typing import List, Dict, Any, Optional


class AegisIndentationLexer:
    """
    A lexer that handles Python-style indentation, producing INDENT and DEDENT tokens
    for the ANTLR4 parser. This is designed specifically for AI code generation
    with clear error messages and position tracking.
    """
    
    # Token types from the grammar
    INDENT_TYPE = 76  # INDENT token type from AegisLangLexer
    DEDENT_TYPE = 77  # DEDENT token type from AegisLangLexer
    COLON_TYPE = 45   # COLON token type from AegisLangLexer

    def __init__(self, lexer):
        """
        Initialize the indentation lexer with an underlying ANTLR4 lexer.
        
        Args:
            lexer: The underlying ANTLR4 lexer that produces tokens
        """
        self.lexer = lexer
        self.indents = [0]          # Indentation stack, starting with 0 (no indent)
        self.indent_errors = []     # Track indentation errors
    
    def process_indentation(self, input_text: str) -> str:
        """
        Process the input text to add explicit INDENT/DEDENT tokens.
        This is a simplified approach that works with the grammar.
        
        Args:
            input_text: The source code to preprocess
            
        Returns:
            The processed source with explicit INDENT and DEDENT tokens
        """
        lines = input_text.split('\n')
        result = []
        indentation_stack = [0]  # Start with 0 indentation
        pending_dedents = 0      # Track pending dedents for empty lines
        
        for i, line in enumerate(lines):
            # Handle empty lines and comments - preserve them but don't change indentation
            stripped = line.strip()
            if not stripped or stripped.startswith('#'):
                result.append(line)
                continue
            
            # Calculate the indentation level (number of spaces)
            indent_level = len(line) - len(line.lstrip())
            content = line.lstrip()
            
            # Check for indentation change
            if indent_level > indentation_stack[-1]:
                # Indentation increased - add INDENT token
                result.append(" " * indent_level + f"INDENT {content}")
                indentation_stack.append(indent_level)
                pending_dedents = 0
            elif indent_level < indentation_stack[-1]:
                # Indentation decreased - add DEDENT tokens
                dedent_count = 0
                while indentation_stack and indent_level < indentation_stack[-1]:
                    indentation_stack.pop()
                    dedent_count += 1
                
                # Check for invalid indentation
                if indent_level not in indentation_stack:
                    # Invalid indentation - add error message
                    error = self._create_indentation_error(indent_level, i+1, 0)
                    self.indent_errors.append(error)
                    # Try to recover by adding the closest valid indentation
                    closest_indent = min(indentation_stack, key=lambda x: abs(x - indent_level))
                    indentation_stack.append(closest_indent)
                
                # Add the right number of DEDENT tokens before the content
                if dedent_count > 0:
                    dedents = " ".join(["DEDENT"] * dedent_count)
                    result.append(" " * indent_level + f"{dedents} {content}")
                    pending_dedents = 0
                else:
                    result.append(line)
            else:
                # No indentation change
                if pending_dedents > 0:
                    # Apply any pending dedents
                    dedents = " ".join(["DEDENT"] * pending_dedents)
                    result.append(" " * indent_level + f"{dedents} {content}")
                    pending_dedents = 0
                else:
                    result.append(line)
        
        # Add any remaining DEDENT tokens at the end
        if len(indentation_stack) > 1:
            for _ in range(len(indentation_stack) - 1):
                result.append("DEDENT")
        
        return '\n'.join(result)
    
    def _create_indentation_error(self, current_indent: int, line: int, column: int) -> Dict[str, Any]:
        """
        Create a detailed error message for indentation issues,
        designed to be AI-friendly with suggestions.
        
        Args:
            current_indent: The current indentation level
            line: Line number with the error
            column: Column number with the error
            
        Returns:
            An error object with details and suggestions
        """
        valid_indents = ", ".join(map(str, self.indents))
        
        # Find closest valid indentation
        closest_indent = min(self.indents, key=lambda x: abs(x - current_indent))
        
        # Basic error message
        message = f"Indentation error at line {line}:{column}: Found indentation of {current_indent} spaces, expected one of [{valid_indents}] spaces."
        
        # Add AI-friendly suggestion
        if current_indent > self.indents[-1]:
            suggestion = f"Indent to exactly {self.indents[-1]} spaces at this level."
        else:
            suggestion = f"Dedent to exactly {closest_indent} spaces to align with the correct block."
        
        # Add code example
        if current_indent > self.indents[-1]:
            example = f"# Instead of this:\n" + \
                      f"{'    ' * (current_indent // 4)}statement\n\n" + \
                      f"# Use this:\n" + \
                      f"{'    ' * (self.indents[-1] // 4)}statement"
        else:
            example = f"# Instead of this:\n" + \
                      f"{'    ' * (current_indent // 4)}statement\n\n" + \
                      f"# Use this:\n" + \
                      f"{'    ' * (closest_indent // 4)}statement"
        
        return {
            "type": "IndentationError",
            "message": message,
            "suggestion": suggestion,
            "example": example,
            "line": line,
            "column": column,
            "current_indent": current_indent,
            "valid_indents": self.indents.copy()
        }


# Legacy IndentationLexer class for backward compatibility
class IndentationLexer:
    """
    Legacy class for backward compatibility. 
    Please use AegisIndentationLexer instead.
    """
    
    def __init__(self, lexer):
        self.lexer = lexer
        self.tokens = []
        self.indents = [0]  # Initial indent level is 0
        self.emit_eof = True
        self.aegis_lexer = AegisIndentationLexer(lexer)
    
    def get_all_tokens(self) -> List[Token]:
        """
        Legacy method for backward compatibility.
        """
        raise NotImplementedError("This method is deprecated. Use AegisIndentationLexer.process_indentation instead.")
    
    def _process_tokens(self, tokens: List[Token]) -> List[Token]:
        """Legacy method, use AegisIndentationLexer instead."""
        raise NotImplementedError("This method is deprecated. Use AegisIndentationLexer.process_indentation instead.")
    
    def _get_indent_size(self, token: Token) -> int:
        """Legacy method, use AegisIndentationLexer instead."""
        raise NotImplementedError("This method is deprecated. Use AegisIndentationLexer.process_indentation instead.")
    
    def _create_token(self, token_type: int, text: str, copy_from: Token = None) -> Token:
        """Legacy method, use AegisIndentationLexer instead."""
        raise NotImplementedError("This method is deprecated. Use AegisIndentationLexer.process_indentation instead.") 