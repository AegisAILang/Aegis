#!/usr/bin/env python3
"""
Test script for the Aegis parser.
This script loads and parses an Aegis file using the ANTLR-based parser.
"""

import os
import sys
import json
from pathlib import Path

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent))

from parser.aegis_parser import AegisParser


def main():
    """Main function to test the parser."""
    if len(sys.argv) < 2:
        print("Usage: python test_parser.py <aegis_file>")
        print("Example: python test_parser.py examples/user_system.ae")
        sys.exit(1)
    
    file_path = sys.argv[1]
    if not os.path.exists(file_path):
        print(f"Error: File '{file_path}' not found.")
        sys.exit(1)
    
    parser = AegisParser()
    try:
        print(f"Parsing file: {file_path}")
        ast = parser.parse_file(file_path)
        
        # Print the AST as formatted JSON
        print("\nParsed AST:")
        print(json.dumps(ast, indent=2))
        
        print("\nParsing completed successfully!")
    except Exception as e:
        print(f"\nError parsing file: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main() 