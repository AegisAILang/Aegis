#!/usr/bin/env python3
"""
Test script for the indentation preprocessor.
"""

import sys
import os
from pathlib import Path

# Add the src directory to the path
script_dir = os.path.dirname(os.path.abspath(__file__))
if script_dir not in sys.path:
    sys.path.insert(0, script_dir)

from lexer.indentation_lexer import AegisIndentationLexer


def main():
    """Test the indentation preprocessor."""
    if len(sys.argv) < 2:
        print("Usage: python test_preprocessor.py <aegis_file>")
        sys.exit(1)
    
    # Read the input file
    with open(sys.argv[1], 'r') as f:
        input_text = f.read()
    
    # Preprocess the input
    preprocessor = AegisIndentationLexer(None)
    output = preprocessor.process_indentation(input_text)
    
    # Print the preprocessed output
    print("Preprocessed output:")
    print("-" * 50)
    print(output)
    print("-" * 50)
    
    # Print any errors
    if preprocessor.indent_errors:
        print("\nIndentation errors:")
        for error in preprocessor.indent_errors:
            print(f"{error['message']}\n{error['suggestion']}")


if __name__ == "__main__":
    main() 