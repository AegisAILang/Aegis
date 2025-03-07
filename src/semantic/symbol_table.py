"""
Symbol Table for Aegis programming language.

This module provides a symbol table implementation for tracking declarations
and their scopes during semantic analysis.
"""

from typing import Dict, List, Any, Optional, Union
from enum import Enum, auto
from dataclasses import dataclass, field

class SymbolType(Enum):
    """Types of symbols that can be stored in the symbol table."""
    VARIABLE = auto()
    FUNCTION = auto()
    TYPE = auto()
    TRAIT = auto()
    MODULE = auto()

@dataclass
class Symbol:
    """
    Represents a symbol in the Aegis language.
    
    Attributes:
        name: The name of the symbol
        symbol_type: The type of symbol (variable, function, etc.)
        type_info: Type information for the symbol
        is_mutable: Whether the symbol can be modified (for variables)
        scope: The scope in which the symbol is defined
    """
    name: str
    symbol_type: SymbolType
    type_info: Any
    is_mutable: bool = False
    scope: str = ""
    
    def __str__(self) -> str:
        return f"{self.name} ({self.symbol_type.name})"

@dataclass
class Scope:
    """
    Represents a lexical scope in the program.
    
    Attributes:
        name: The name of the scope
        parent: The parent scope, or None for global scope
        symbols: Mapping of symbol names to Symbol objects
        children: Child scopes
    """
    name: str
    parent: Optional['Scope'] = None
    symbols: Dict[str, Symbol] = field(default_factory=dict)
    children: List['Scope'] = field(default_factory=list)
    
    def add_symbol(self, symbol: Symbol) -> None:
        """Add a symbol to this scope."""
        self.symbols[symbol.name] = symbol
    
    def lookup_local(self, name: str) -> Optional[Symbol]:
        """Look up a symbol only in this scope."""
        return self.symbols.get(name)
    
    def __str__(self) -> str:
        return f"Scope({self.name}, {len(self.symbols)} symbols)"

class SymbolTable:
    """
    Symbol table for tracking declarations and their scopes.
    
    The symbol table maintains a hierarchy of scopes and allows looking up
    symbols in the current and parent scopes.
    """
    
    def __init__(self):
        """Initialize an empty symbol table with a global scope."""
        self.global_scope = Scope("global")
        self.current_scope = self.global_scope
        self.scope_stack = [self.global_scope]
    
    def enter_scope(self, name: str) -> None:
        """
        Enter a new scope.
        
        Args:
            name: The name of the new scope
        """
        new_scope = Scope(name, parent=self.current_scope)
        self.current_scope.children.append(new_scope)
        self.current_scope = new_scope
        self.scope_stack.append(new_scope)
    
    def exit_scope(self) -> None:
        """Exit the current scope and return to the parent scope."""
        if len(self.scope_stack) > 1:
            self.scope_stack.pop()
            self.current_scope = self.scope_stack[-1]
    
    def add_symbol(self, name: str, symbol_type: SymbolType, type_info: Any, is_mutable: bool = False) -> Symbol:
        """
        Add a symbol to the current scope.
        
        Args:
            name: The name of the symbol
            symbol_type: The type of symbol (variable, function, etc.)
            type_info: Type information for the symbol
            is_mutable: Whether the symbol can be modified (for variables)
            
        Returns:
            The created Symbol object
        """
        symbol = Symbol(
            name=name,
            symbol_type=symbol_type,
            type_info=type_info,
            is_mutable=is_mutable,
            scope=self.current_scope.name
        )
        self.current_scope.add_symbol(symbol)
        return symbol
    
    def lookup(self, name: str) -> Optional[Symbol]:
        """
        Look up a symbol in the current scope and its ancestors.
        
        Args:
            name: The name of the symbol to look up
            
        Returns:
            The Symbol object if found, None otherwise
        """
        # Look in current scope and parent scopes
        scope = self.current_scope
        while scope:
            symbol = scope.lookup_local(name)
            if symbol:
                return symbol
            scope = scope.parent
        
        return None
    
    def lookup_in_scope(self, name: str, scope_name: str) -> Optional[Symbol]:
        """
        Look up a symbol in a specific scope.
        
        Args:
            name: The name of the symbol to look up
            scope_name: The name of the scope to look in
            
        Returns:
            The Symbol object if found, None otherwise
        """
        # Find the scope with the given name
        scope_to_check = self._find_scope(self.global_scope, scope_name)
        if not scope_to_check:
            return None
        
        return scope_to_check.lookup_local(name)
    
    def _find_scope(self, current: Scope, name: str) -> Optional[Scope]:
        """Recursively find a scope by name."""
        if current.name == name:
            return current
        
        for child in current.children:
            result = self._find_scope(child, name)
            if result:
                return result
        
        return None
    
    def get_all_symbols(self) -> List[Symbol]:
        """Get all symbols defined in all scopes."""
        symbols = []
        self._collect_symbols(self.global_scope, symbols)
        return symbols
    
    def _collect_symbols(self, scope: Scope, symbols: List[Symbol]) -> None:
        """Recursively collect symbols from a scope and its children."""
        symbols.extend(scope.symbols.values())
        
        for child in scope.children:
            self._collect_symbols(child, symbols)
    
    def get_current_scope_name(self) -> str:
        """Get the name of the current scope."""
        return self.current_scope.name
    
    def get_scope_path(self) -> str:
        """Get the full path of the current scope."""
        path = []
        scope = self.current_scope
        
        while scope:
            path.insert(0, scope.name)
            scope = scope.parent
        
        return ".".join(path) 