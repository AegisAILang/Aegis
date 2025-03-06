#!/bin/bash
echo "Installing Aegis dependencies..."
pip install llvmlite pandas ace_tools  # or wherever your dependencies live
# Possibly: apt-get install clang, etc.

echo "Aegis installation complete!"
