import re
from utils.logger import get_logger

logger = get_logger(__name__)
# -------------------------------
# Lexer Implementation
# -------------------------------
# Token definitions: keywords, types, operators, symbols.
# A lex() function that scans the source code and returns tokens.
TOKEN_TYPES = {
    "KEYWORDS": [
        "fn",
        "struct",
        "enum",
        "return",
        "if",
        "else",
        "elif",
        "for",
        "while",
        "module",
        "let",
        "mut",
        "async",
        "await",
        "task",
    ],
    "TYPES": [
        "int",
        "float",
        "bool",
        "char",
        "string",
        "List",
        "Array",
        "Map",
        "Option",
        "Result",
    ],
    "OPERATORS": [
        "+",
        "-",
        "*",
        "/",
        "=",
        "==",
        "!=",
        ">=",
        "<=",
        "<",
        ">",
        "->",
        "::",
    ],
    "SYMBOLS": [":", ",", "(", ")", "[", "]", "{", "}", "...", "parallel"],
}

TOKEN_PATTERNS = [
    (
        r"\b(fn|struct|enum|return|if|else|elif|for|while|module|let|mut|async|await|task)\b",
        "KEYWORD",
    ),
    (r"\b(int|float|bool|char|string|List|Array|Map|Option|Result)\b", "TYPE"),
    (r"\b[0-9]+\b", "NUMBER"),
    (r"\b[a-zA-Z_][a-zA-Z0-9_]*\b", "IDENTIFIER"),
    (r'".*?"', "STRING"),
    (r"#[^\n]*", "COMMENT"),
    (r"[\+\-\*/=<>!:]+", "OPERATOR"),
    (r"[\(\)\[\]\{\},:]", "SYMBOL"),
    (r"\s+", None),  # Ignore whitespace
]


# -------------------------------
# Lexer Function
# -------------------------------
def lex(input_code):
    """Enhanced lexer with better error handling and context."""
    logger.info("Starting lexer...")
    tokens = []
    line_num = 1
    column = 1
    input_len = len(input_code)
    idx = 0

    while idx < input_len:
        match_found = False

        # Track line numbers
        if input_code[idx] == "\n":
            line_num += 1
            column = 1
            idx += 1
            continue

        for pattern, token_type in TOKEN_PATTERNS:
            match = re.match(pattern, input_code[idx:])
            if match:
                if token_type:  # Skip whitespace
                    tokens.append((token_type, match.group(0), line_num, column))
                    logger.debug(f"Token: {token_type}, {match.group(0)}, {line_num}, {column}")
                idx += len(match.group(0))
                column += len(match.group(0))
                match_found = True
                break

        if not match_found:
            logger.error(f"No match found for line {line_num}, column {column}")
            # Extract a snippet of the problematic code for context
            context_start = max(0, idx - 10)
            context_end = min(len(input_code), idx + 10)
            context = input_code[context_start:context_end]
            position_marker = " " * (min(10, idx - context_start)) + "^"

            error_msg = (
                f"Lexical error at line {line_num}, column {column}:\n"
                f"{context}\n{position_marker}\n"
                f"Unexpected character: '{input_code[idx]}'"
            )
            raise SyntaxError(error_msg)
    logger.debug(f"Lexer tokens: {len(tokens)} tokens.")
    logger.info("Lexer completed successfully.")
    return tokens


# Lexing with indentation (if you want indentation-based blocks).
# By default, you don't need this for your current grammar. If you keep it, define `lex_line`.
def lex_line(line_content, line_num):
    """
    A helper to tokenize a single line (used by lex_with_indentation).
    Mirrors the `lex` logic but for one line.
    """
    logger.info("Starting lex_line...")
    tokens = []
    idx = 0
    column = 1
    length = len(line_content)

    while idx < length:
        match_found = False
        if line_content[idx] == "\n":
            # not strictly needed here
            idx += 1
            column = 1
            continue

        for pattern, token_type in TOKEN_PATTERNS:
            match = re.match(pattern, line_content[idx:])
            if match:
                if token_type:
                    tokens.append((token_type, match.group(0), line_num, column))
                idx += len(match.group(0))
                column += len(match.group(0))
                match_found = True
                break

        if not match_found:
            logger.error(f"No match found for line {line_num}, column {column}")
            context_start = max(0, idx - 10)
            context_end = min(length, idx + 10)
            context = line_content[context_start:context_end]
            position_marker = " " * (min(10, idx - context_start)) + "^"

            error_msg = (
                f"Lexical error at line {line_num}, column {column}:\n"
                f"{context}\n{position_marker}\n"
                f"Unexpected character: '{line_content[idx]}'"
            )
            raise SyntaxError(error_msg)
    logger.debug(f"Lexed line {line_num}: {tokens}")
    return tokens


def lex_with_indentation(input_code):
    """Lexer that handles indentation levels for scoping."""
    logger.info("Starting lex_with_indentation...")
    tokens = []
    lines = input_code.splitlines()

    # Track indentation stack
    indent_stack = [0]  # Start with 0 indentation

    for line_num, line in enumerate(lines, 1):
        # Skip empty lines
        if not line.strip():
            continue

        # Calculate indentation level
        indent = len(line) - len(line.lstrip())
        line_content = line.lstrip()

        # Skip comment-only lines
        if line_content.startswith("#"):
            continue

        # Handle indentation changes
        if indent > indent_stack[-1]:
            # Indentation increased - push new level and emit INDENT token
            indent_stack.append(indent)
            tokens.append(("INDENT", "", line_num, 0))
        elif indent < indent_stack[-1]:
            # Indentation decreased - pop levels and emit DEDENT tokens
            while indent < indent_stack[-1]:
                indent_stack.pop()
                tokens.append(("DEDENT", "", line_num, 0))

            # Ensure indent level matches exactly one of the previous levels
            if indent != indent_stack[-1]:
                # invalid indent
                raise IndentationError(
                    f"Line {line_num}: Invalid indentation level (got {indent}, expected {indent_stack[-1]})"
                )

        # Now lex the actual content of the line
        line_tokens = lex_line(line_content, line_num)
        tokens.extend(line_tokens)

        # Add implicit line end
        tokens.append(("NEWLINE", "\n", line_num, len(line)))

    # Add any remaining DEDENT tokens at the end of the file
    while len(indent_stack) > 1:
        indent_stack.pop()
        tokens.append(("DEDENT", "", len(lines) + 1, 0))

    logger.debug(f"Lexed with indentation: {tokens}")
    return tokens