from abc import ABC, abstractmethod
from typing import Optional, OrderedDict
from lexical_analysis.tokens import TokenType


class Symbol(ABC):
    """
    Abstract base class representing a symbol in the symbol table.

    A symbol represents any named entity in the programming language, such as
    variables, procedures, functions, types, or program names. This base class
    provides the common interface and behavior shared by all symbol types.

    The symbol hierarchy uses the Template Method pattern - concrete subclasses
    implement the abstract methods __repr__ and __str__ to provide specific
    string representations, while the base class handles common functionality
    like name storage.

    Attributes:
        name: The identifier name of the symbol as it appears in source code
    """

    # Use __slots__ for memory efficiency - restricts instance attributes
    __slots__ = ("name",)

    def __init__(self, name: str) -> None:
        """
        Initialize a symbol with its name.

        Args:
            name: The identifier name of this symbol
        """
        self.name: str = name

    @abstractmethod
    def __repr__(self) -> str:
        """
        Return a developer-friendly string representation of the symbol.

        This should include the symbol type and all relevant attributes,
        formatted for debugging and development purposes.

        Returns:
            String suitable for debugging and logging
        """
        pass

    @abstractmethod
    def __str__(self) -> str:
        """
        Return a human-readable string representation of the symbol.

        This should provide a clear, user-friendly description of what
        the symbol represents, suitable for error messages and output.

        Returns:
            String suitable for user-facing messages
        """
        pass


class TypelessSymbol(Symbol):
    """
    Base class for symbols that don't have an associated data type.

    This includes program names, built-in type names, and procedure names.
    These symbols represent entities that exist in the language but don't
    have a data type in the traditional sense (unlike variables which
    have types like INTEGER or REAL).

    This class serves as an intermediate abstraction to distinguish between
    symbols that have types (variables, functions) and those that don't.
    """

    # No additional slots needed - inherits name from Symbol
    __slots__ = ()


class TypedSymbol(Symbol):
    """
    Base class for symbols that have an associated data type.

    This includes variables and functions, which have specific data types
    like INTEGER, REAL, or user-defined types. The type information is
    essential for semantic analysis, type checking, and code generation.

    Attributes:
        name: Inherited from Symbol - the identifier name
        type: The data type name (e.g., "INTEGER", "REAL", custom type name)
    """

    # Add type slot in addition to inherited name slot
    __slots__ = ("type",)

    def __init__(self, name: str, type: str) -> None:
        """
        Initialize a typed symbol with name and type.

        Args:
            name: The identifier name of this symbol
            type: The data type name (e.g., "INTEGER", "REAL")
        """
        super().__init__(name)
        self.type: str = type


class ProgramSymbol(TypelessSymbol):
    """
    Represents a program name in the symbol table.

    In Pascal-like languages, the program has a name declared at the top
    (e.g., "PROGRAM HelloWorld;"). This symbol stores that program name
    for reference during compilation and potential linking phases.

    Example:
        For "PROGRAM Calculator;" -> ProgramSymbol(name="Calculator")
    """

    def __repr__(self) -> str:
        """Return developer-friendly representation showing symbol type and name."""
        return f"{self.__class__.__name__}(name='{self.name}')"

    def __str__(self) -> str:
        """Return user-friendly representation identifying this as a program."""
        return f"Program: {self.name}"


class BuiltInTypeSymbol(TypelessSymbol):
    """
    Represents a built-in data type in the symbol table.

    Built-in types are fundamental types provided by the language itself,
    such as INTEGER, REAL, BOOLEAN, etc. These symbols are automatically
    added to the global scope and serve as type references for variable
    declarations and type checking.

    The language's type system relies on these symbols to validate that
    variables are declared with valid types and to perform type checking
    during semantic analysis.

    Example:
        For INTEGER type -> BuiltInTypeSymbol(name="INTEGER")
    """

    def __repr__(self) -> str:
        """Return developer-friendly representation showing this is a built-in type."""
        return f"{self.__class__.__name__}(name='{self.name}')"

    def __str__(self) -> str:
        """Return user-friendly representation identifying this as a built-in type."""
        return f"Built-in type: {self.name}"


class VariableSymbol(TypedSymbol):
    """
    Represents a variable declaration in the symbol table.

    Variables are named storage locations with specific data types. This symbol
    stores both the variable name and its declared type, which is essential for:
    - Type checking during semantic analysis
    - Memory allocation during code generation
    - Scope resolution during compilation

    Example:
        For "VAR count: INTEGER;" -> VariableSymbol(name="count", type="INTEGER")
    """

    def __repr__(self) -> str:
        """Return developer-friendly representation showing variable name and type."""
        return f"{self.__class__.__name__}(name='{self.name}', type='{self.type}')"

    def __str__(self) -> str:
        """Return user-friendly representation showing variable with its type."""
        return f"Variable: {self.name} -> {self.type}"


class ProcedureSymbol(TypelessSymbol):
    """
    Represents a procedure declaration in the symbol table.

    Procedures are subroutines that perform actions but don't return values.
    This symbol stores the procedure name and its parameter list, which is
    needed for:
    - Parameter count and type validation during procedure calls
    - Scope management (procedures create new scopes)
    - Code generation for procedure calls and definitions

    Procedures are typeless because they don't return values (unlike functions).

    Attributes:
        name: Inherited from Symbol - the procedure name
        parameters: List of VariableSymbol objects representing formal parameters

    Example:
        For "PROCEDURE DrawLine(x1, y1, x2, y2: INTEGER);" ->
        ProcedureSymbol(name="DrawLine", parameters=[x1:INTEGER, y1:INTEGER, ...])
    """

    # Add parameters slot in addition to inherited name slot
    __slots__ = ("parameters",)

    def __init__(self, name: str, parameters: list[VariableSymbol]) -> None:
        """
        Initialize a procedure symbol with name and parameter list.

        Args:
            name: The procedure name
            parameters: List of VariableSymbol objects for formal parameters
        """
        super().__init__(name)
        self.parameters: list[VariableSymbol] = parameters

    def __repr__(self) -> str:
        """Return developer-friendly representation with procedure name and parameters."""
        return (
            f"{self.__class__.__name__}(name={self.name}, parameters={self.parameters})"
        )

    def __str__(self) -> str:
        """Return user-friendly representation showing procedure signature."""
        # Format parameters as "name: type" pairs for readability
        params_str = ", ".join(
            [f"{param.name}: {param.type}" for param in self.parameters]
        )
        return f"Procedure: {self.name}({params_str})"


class FunctionSymbol(TypedSymbol):
    """
    Represents a function declaration in the symbol table.

    Functions are subroutines that return values of a specific type. This symbol
    stores the function name, return type, and parameter list, which is needed for:
    - Return type validation during function calls
    - Parameter count and type validation during function calls
    - Scope management (functions create new scopes)
    - Code generation for function calls and definitions

    Functions are typed symbols because they return values of specific types.

    Attributes:
        name: Inherited from Symbol - the function name
        type: Inherited from TypedSymbol - the return type
        parameters: List of VariableSymbol objects representing formal parameters

    Example:
        For "FUNCTION Max(a, b: INTEGER): INTEGER;" ->
        FunctionSymbol(name="Max", parameters=[a:INTEGER, b:INTEGER], type="INTEGER")
    """

    # Add parameters slot in addition to inherited name and type slots
    __slots__ = ("parameters",)

    def __init__(self, name: str, parameters: list[VariableSymbol], type: str) -> None:
        """
        Initialize a function symbol with name, parameters, and return type.

        Args:
            name: The function name
            parameters: List of VariableSymbol objects for formal parameters
            type: The return type name (e.g., "INTEGER", "REAL")
        """
        super().__init__(name, type)
        self.parameters: list[VariableSymbol] = parameters

    def __repr__(self) -> str:
        """Return developer-friendly representation with all function details."""
        return f"{self.__class__.__name__}(name='{self.name}', parameters={self.parameters}, type='{self.type}')"

    def __str__(self) -> str:
        """Return user-friendly representation showing function signature and return type."""
        # Format parameters as "name: type" pairs for readability
        params_str = ", ".join(
            [f"{param.name}: {param.type}" for param in self.parameters]
        )
        return f"Function: {self.name}({params_str}) -> {self.type}"


class ScopedSymbolTable:
    """
    A symbol table that supports nested scopes and lexical scoping rules.

    This class implements a scoped symbol table for managing symbol visibility
    and lifetime in a programming language with nested scopes (like Pascal).
    It supports:
    - Hierarchical scope management (global, procedure, function scopes)
    - Symbol definition and lookup with scope resolution
    - Built-in type management
    - Scope chain traversal for identifier resolution

    The symbol table uses lexical scoping rules where inner scopes can access
    symbols from outer scopes, but not vice versa. Symbol lookup starts in
    the current scope and walks up the scope chain until a symbol is found
    or the global scope is exhausted.

    Attributes:
        _symbols: Ordered dictionary mapping symbol names to Symbol objects
        scope_name: Human-readable name for this scope (e.g., "global", "procedure_name")
        scope_level: Numeric level in scope hierarchy (0=global, 1=first nested, etc.)
        enclosing_scope: Reference to parent scope, None for global scope

    Design Notes:
        - Uses OrderedDict to preserve symbol definition order for debugging
        - Built-in types are automatically added to global scope (level 0)
        - Supports both current-scope-only and scope-chain lookup modes
    """

    # Use __slots__ for memory efficiency
    __slots__ = ("_symbols", "scope_name", "scope_level", "enclosing_scope")

    # Class-level constant defining built-in types available in the language
    # These are automatically added to the global scope for type checking
    BUILT_IN_TYPES: list[BuiltInTypeSymbol] = [
        BuiltInTypeSymbol(TokenType.INTEGER.name),  # INTEGER type
        BuiltInTypeSymbol(TokenType.REAL.name),  # REAL type
    ]

    def __init__(
        self,
        scope_name: str,
        scope_level: int,
        enclosing_scope: Optional["ScopedSymbolTable"],
    ) -> None:
        """
        Initialize a new symbol table scope.

        Args:
            scope_name: Human-readable name for this scope (for debugging)
            scope_level: Numeric level (0=global, higher=more nested)
            enclosing_scope: Parent scope reference, None for global scope
        """
        # OrderedDict preserves insertion order for consistent debugging output
        self._symbols: OrderedDict[str, Symbol] = OrderedDict()
        self.scope_name: str = scope_name
        self.scope_level: int = scope_level
        self.enclosing_scope: Optional[ScopedSymbolTable] = enclosing_scope

        # Global scope (level 0) gets built-in types automatically
        if scope_level == 0:
            self._init_builtins()

    def __repr__(self) -> str:
        """Return developer-friendly representation showing scope details."""
        return f"{self.__class__.__name__}(scope_name={self.scope_name}, scope_level={self.scope_level})"

    def __str__(self) -> str:
        """Return human-readable representation showing all symbols in this scope."""
        return f"Symbols: {[str(value) for value in self._symbols.values()]}"

    def _init_builtins(self) -> None:
        """
        Initialize the global scope with built-in type symbols.

        This method is called automatically when creating the global scope
        (scope_level == 0). It adds all built-in types like INTEGER and REAL
        to the symbol table so they can be referenced in variable declarations
        and type checking.

        Built-in types are essential for the language's type system and must
        be available in the global scope for all code to reference.
        """
        for builtin_type in self.BUILT_IN_TYPES:
            self.define(builtin_type)

    def define(self, symbol: Symbol) -> None:
        """
        Add a symbol definition to this scope.

        This method adds a new symbol to the current scope's symbol table.
        If a symbol with the same name already exists in this scope, it will
        be replaced (though this typically represents a semantic error that
        should be caught during semantic analysis).

        Args:
            symbol: The Symbol object to add to this scope

        Note:
            This method only adds symbols to the current scope, not parent scopes.
            Symbol shadowing (hiding parent scope symbols with same name) is
            handled naturally by the lookup mechanism.
        """
        self._symbols[symbol.name] = symbol

    def lookup(self, name: str, current_scope_only: bool = False) -> Optional[Symbol]:
        """
        Look up a symbol by name, following lexical scoping rules.

        This method implements lexical scoping by searching for a symbol starting
        in the current scope and walking up the scope chain until found or exhausted.
        This allows inner scopes to access symbols from outer scopes while
        maintaining proper encapsulation.

        The lookup process:
        1. Check current scope's symbol table
        2. If found, return the symbol
        3. If not found and current_scope_only=True, return None
        4. If not found and we have an enclosing scope, recursively search parent
        5. If no enclosing scope exists, return None (symbol not found)

        Args:
            name: The symbol name to search for
            current_scope_only: If True, only search current scope (no chain traversal)

        Returns:
            The Symbol object if found, None if not found

        Examples:
            lookup("x")              # Search current scope and all parent scopes
            lookup("x", True)        # Search only current scope
        """
        # First, check if symbol exists in current scope
        symbol: Optional[Symbol] = self._symbols.get(name)
        if symbol is not None:
            return symbol

        # If we only want current scope, stop here
        if current_scope_only:
            return None

        # If we have an enclosing scope, recursively search up the chain
        if self.enclosing_scope is not None:
            return self.enclosing_scope.lookup(name)

        # Symbol not found in any scope
        return None
