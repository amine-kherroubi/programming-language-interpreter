from abc import ABC, abstractmethod
from typing import Optional
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

    def __init__(self, name: str) -> None:
        super().__init__(name)


class TypedSymbol(Symbol):
    __slots__ = ("type",)

    def __init__(self, name: str, type: str) -> None:
        super().__init__(name)
        self.type: str = type


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


class SymbolTable_(object):
    BUILT_IN_TYPES: list[BuiltInTypeSymbol] = [
        BuiltInTypeSymbol(TokenType.INTEGER.name),
        BuiltInTypeSymbol(TokenType.REAL.name),
    ]

    def __init__(self) -> None:
        self._symbols: dict[str, Symbol] = {}
        self._init_builtins()

    def __repr__(self) -> str:
        return "SymbolTable()"

    def __str__(self) -> str:
        return f"Symbols: {[str(value) for value in self._symbols.values()]}"

    def _init_builtins(self) -> None:
        for builtin_type in self.BUILT_IN_TYPES:
            self.define(builtin_type)

    def define(self, symbol: Symbol) -> None:
        self._symbols[symbol.name] = symbol

    def lookup(self, name: str) -> Optional[Symbol]:
        return self._symbols.get(name)
