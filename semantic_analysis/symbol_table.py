from abc import ABC, abstractmethod
from typing import Optional, OrderedDict
from lexical_analysis.tokens import TokenType
from syntactic_analysis.ast import NodeBlock


class Symbol(ABC):
    __slots__ = ("identifier",)

    def __init__(self, identifier: str) -> None:
        self.identifier = identifier

    @abstractmethod
    def __repr__(self) -> str: ...

    @abstractmethod
    def __str__(self) -> str: ...


class TypelessSymbol(Symbol):
    __slots__ = ()


class TypedSymbol(Symbol):
    __slots__ = ("type",)

    def __init__(self, identifier: str, symbol_type: str) -> None:
        super().__init__(identifier)
        self.type = symbol_type


class BuiltInTypeSymbol(TypelessSymbol):
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(identifier='{self.identifier}')"

    def __str__(self) -> str:
        return f"<BUILT-IN: {self.identifier}>"


class VariableSymbol(TypedSymbol):
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(identifier='{self.identifier}', type='{self.type}')"

    def __str__(self) -> str:
        return f"<VARIABLE: {self.identifier}, {self.type}>"


class ConstantSymbol(TypedSymbol):
    __slots__ = ("is_constant",)

    def __init__(self, identifier: str, symbol_type: str) -> None:
        super().__init__(identifier, symbol_type)
        self.is_constant = True

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(identifier='{self.identifier}', type='{self.type}')"

    def __str__(self) -> str:
        return f"<CONSTANT: {self.identifier}, {self.type}>"


class FunctionSymbol(Symbol):
    __slots__ = ("parameters", "return_type", "block")

    def __init__(
        self,
        identifier: str,
        parameters: Optional[list[VariableSymbol]],
        return_type: str,
        block: NodeBlock,
    ) -> None:
        super().__init__(identifier)
        self.parameters = parameters
        self.return_type = return_type
        self.block = block

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(identifier='{self.identifier}', parameters={self.parameters}, return_type='{self.return_type}')"

    def __str__(self) -> str:
        params = (
            ", ".join(f"{p.identifier}: {p.type}" for p in self.parameters)
            if self.parameters
            else ""
        )
        return f"<FUNCTION: {self.identifier}({params}) -> {self.return_type}>"


class ProcedureSymbol(Symbol):
    __slots__ = ("parameters", "block")

    def __init__(
        self,
        identifier: str,
        parameters: Optional[list[VariableSymbol]],
        block: NodeBlock,
    ) -> None:
        super().__init__(identifier)
        self.parameters = parameters
        self.block = block

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(identifier='{self.identifier}', parameters={self.parameters})"

    def __str__(self) -> str:
        params = (
            ", ".join(f"{p.identifier}: {p.type}" for p in self.parameters)
            if self.parameters
            else ""
        )
        return f"<PROCEDURE: {self.identifier}({params})>"


class ScopedSymbolTable:
    __slots__ = ("_symbols", "scope_name", "scope_level", "enclosing_scope")

    BUILT_IN_TYPES: list[BuiltInTypeSymbol] = [
        BuiltInTypeSymbol(TokenType.INT_TYPE.value),
        BuiltInTypeSymbol(TokenType.FLOAT_TYPE.value),
        BuiltInTypeSymbol(TokenType.STRING_TYPE.value),
        BuiltInTypeSymbol(TokenType.BOOL_TYPE.value),
    ]

    def __init__(
        self,
        scope_name: str,
        scope_level: int,
        enclosing_scope: Optional["ScopedSymbolTable"],
    ) -> None:
        self.scope_name = scope_name
        self.scope_level = scope_level
        self.enclosing_scope = enclosing_scope
        self._symbols: OrderedDict[str, Symbol] = OrderedDict()

        if scope_level == 1:
            self._init_builtins()

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(scope_name='{self.scope_name}', scope_level={self.scope_level})"

    def __str__(self) -> str:
        symbols = ", ".join(str(symbol) for symbol in self._symbols.values())
        return f"Scope '{self.scope_name}' (level {self.scope_level}): [{symbols}]"

    def _init_builtins(self) -> None:
        for builtin in self.BUILT_IN_TYPES:
            self.define(builtin)

    def define(self, symbol: Symbol) -> None:
        self._symbols[symbol.identifier] = symbol

    def lookup(self, name: str, current_scope_only: bool = False) -> Optional[Symbol]:
        symbol = self._symbols.get(name)
        if symbol:
            return symbol
        if not current_scope_only and self.enclosing_scope:
            return self.enclosing_scope.lookup(name)
        return None

    def lookup_callable(self, name: str) -> Optional[Symbol]:
        symbol = self.lookup(name)
        if isinstance(symbol, (FunctionSymbol, ProcedureSymbol)):
            return symbol
        return None
