from abc import ABC, abstractmethod
from typing import Optional, OrderedDict
from lexical_analysis.tokens import TokenType


class Symbol(ABC):
    __slots__ = ("name",)

    def __init__(self, name: str) -> None:
        self.name: str = name

    @abstractmethod
    def __repr__(self) -> str:
        pass

    @abstractmethod
    def __str__(self) -> str:
        pass


class TypelessSymbol(Symbol):
    __slots__ = ()


class TypedSymbol(Symbol):
    __slots__ = ("type",)

    def __init__(self, name: str, type: str) -> None:
        super().__init__(name)
        self.type: str = type


class ProgramSymbol(TypelessSymbol):
    def __repr__(self) -> str:
        return f"ProgramSymbol(name='{self.name}')"

    def __str__(self) -> str:
        return f"Program: {self.name}"


class BuiltInTypeSymbol(TypelessSymbol):
    def __repr__(self) -> str:
        return f"BuiltInTypeSymbol(name='{self.name}')"

    def __str__(self) -> str:
        return f"Built-in type: {self.name}"


class VariableSymbol(TypedSymbol):
    def __repr__(self) -> str:
        return f"VariableSymbol(name='{self.name}', type='{self.type}')"

    def __str__(self) -> str:
        return f"Variable: {self.name} -> {self.type}"


class ProcedureSymbol(TypelessSymbol):
    __slots__ = ("parameters",)

    def __init__(self, name: str, parameters: list[VariableSymbol]) -> None:
        super().__init__(name)
        self.parameters: list[VariableSymbol] = parameters

    def __repr__(self) -> str:
        return f"ProcedureSymbol(name={self.name}, parameters={self.parameters})"

    def __str__(self) -> str:
        params_str = ", ".join(
            [f"{param.name}: {param.type}" for param in self.parameters]
        )
        return f"Procedure: {self.name}({params_str})"


class FunctionSymbol(TypedSymbol):
    __slots__ = ("parameters",)

    def __init__(self, name: str, parameters: list[VariableSymbol], type: str) -> None:
        super().__init__(name, type)
        self.parameters: list[VariableSymbol] = parameters

    def __repr__(self) -> str:
        return f"FunctionSymbol(name='{self.name}', parameters={self.parameters}, type='{self.type}')"

    def __str__(self) -> str:
        params_str = ", ".join(
            [f"{param.name}: {param.type}" for param in self.parameters]
        )
        return f"Function: {self.name}({params_str}) -> {self.type}"


class ScopedSymbolTable:
    __slots__ = ("_symbols", "scope_name", "scope_level", "enclosing_scope")

    BUILT_IN_TYPES: list[BuiltInTypeSymbol] = [
        BuiltInTypeSymbol(TokenType.INTEGER.name),
        BuiltInTypeSymbol(TokenType.REAL.name),
    ]

    def __init__(
        self,
        scope_name: str,
        scope_level: int,
        enclosing_scope: Optional["ScopedSymbolTable"],
    ) -> None:
        self._symbols: OrderedDict[str, Symbol] = OrderedDict()
        self.scope_name: str = scope_name
        self.scope_level: int = scope_level
        self.enclosing_scope: Optional[ScopedSymbolTable] = enclosing_scope
        if scope_level == 0:
            self._init_builtins()

    def __repr__(self) -> str:
        return f"ScopedSymbolTable(scope_name={self.scope_name}, scope_level={self.scope_level})"

    def __str__(self) -> str:
        return f"Symbols: {[str(value) for value in self._symbols.values()]}"

    def _init_builtins(self) -> None:
        for builtin_type in self.BUILT_IN_TYPES:
            self.define(builtin_type)

    def define(self, symbol: Symbol) -> None:
        self._symbols[symbol.name] = symbol

    def lookup(self, name: str) -> Optional[Symbol]:
        symbol: Optional[Symbol] = self._symbols.get(name)
        if symbol is not None:
            return symbol
        if self.enclosing_scope is not None:
            return self.enclosing_scope.lookup(name)
        return None
