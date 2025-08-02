from abc import ABC, abstractmethod
from typing import Optional
from lexical_analysis.tokens import TokenType


class Symbol(ABC):
    __slots__ = ("name", "type")

    def __init__(self, name: str, type: Optional[str] = None) -> None:
        self.name: str = name
        self.type: Optional[str] = type

    @abstractmethod
    def __repr__(self) -> str:
        pass


class BuiltInTypeSymbol(Symbol):
    def __init__(self, name: str) -> None:
        super().__init__(name)

    def __repr__(self) -> str:
        return f"BuiltInTypeSymbol(name={self.name}, type={self.type})"

    def __str__(self) -> str:
        return f"Built-in: {self.name}"


class VariableSymbol(Symbol):
    def __repr__(self) -> str:
        return f"VariableSymbol(name={self.name}, type={self.type})"

    def __str__(self) -> str:
        return f"Variable: {self.name}, {self.type}"


class SymbolTable_(object):
    BUILT_IN_TYPES: list[BuiltInTypeSymbol] = [
        BuiltInTypeSymbol(TokenType.INTEGER.name),
        BuiltInTypeSymbol(TokenType.REAL.name),
    ]

    def __init__(self) -> None:
        self._symbols: dict[str, Symbol] = {}

    def __repr__(self) -> str:
        return f"SymbolTable()"

    def __str__(self) -> str:
        return f"Symbols: {[str(value) for value in self._symbols.values()]}"

    def _init_builtins(self):
        for type in self.BUILT_IN_TYPES:
            self.define(type)

    def define(self, symbol: Symbol) -> None:
        self._symbols[symbol.name] = symbol

    def lookup(self, name: str) -> Optional[Symbol]:
        return self._symbols.get(name)
