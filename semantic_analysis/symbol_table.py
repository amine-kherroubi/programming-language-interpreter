from abc import ABC, abstractmethod
from typing import Optional, OrderedDict
from lexical_analysis.tokens import TokenType
from syntactic_analysis.ast import NodeBlock


class Symbol(ABC):
    __slots__ = ("identifier",)

    def __init__(self, identifier: str) -> None:
        self.identifier: str = identifier

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

    def __init__(self, identifier: str, type: str) -> None:
        super().__init__(identifier)
        self.type: str = type


class BuiltInTypeSymbol(TypelessSymbol):
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(identifier='{self.identifier}')"

    def __str__(self) -> str:
        return f"Built-in type: {self.identifier}"


class VariableSymbol(TypedSymbol):
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(identifier='{self.identifier}', type='{self.type}')"

    def __str__(self) -> str:
        return f"Variable: {self.identifier} -> {self.type}"


class ConstantSymbol(TypedSymbol):
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(identifier='{self.identifier}', type='{self.type}')"

    def __str__(self) -> str:
        return f"Constant: {self.identifier} -> {self.type}"


class UnitSymbol(TypedSymbol):
    __slots__ = ("parameters", "gives_type", "block")

    def __init__(
        self,
        identifier: str,
        parameters: list[VariableSymbol],
        gives_type: Optional[str],
        block: NodeBlock,
    ) -> None:
        super().__init__(identifier, TokenType.UNIT_TYPE.value)
        self.parameters: list[VariableSymbol] = parameters
        self.gives_type: Optional[str] = gives_type
        self.block: NodeBlock = block

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(identifier={self.identifier}, parameters={self.parameters}, gives_type={self.gives_type}, block={self.block})"

    def __str__(self) -> str:
        params_str = ", ".join(
            [f"{param.identifier}: {param.type}" for param in self.parameters]
        )
        gives_str = f" -> {self.gives_type}" if self.gives_type else ""
        return f"Unit: {self.identifier}({params_str}){gives_str}"


class ScopedSymbolTable:
    __slots__ = ("_symbols", "scope_name", "scope_level", "enclosing_scope")

    BUILT_IN_TYPES: list[BuiltInTypeSymbol] = [
        BuiltInTypeSymbol(TokenType.WHOLE_TYPE.value),
        BuiltInTypeSymbol(TokenType.REAL_TYPE.value),
        BuiltInTypeSymbol(TokenType.UNIT_TYPE.value),
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
        if scope_level == 1:
            self._init_builtins()

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(scope_name={self.scope_name}, scope_level={self.scope_level})"

    def __str__(self) -> str:
        return f"Symbols: {[str(value) for value in self._symbols.values()]}"

    def _init_builtins(self) -> None:
        for builtin_type in self.BUILT_IN_TYPES:
            self.define(builtin_type)

    def define(self, symbol: Symbol) -> None:
        self._symbols[symbol.identifier] = symbol

    def lookup(self, name: str, current_scope_only: bool = False) -> Optional[Symbol]:
        symbol: Optional[Symbol] = self._symbols.get(name)
        if symbol is not None:
            return symbol
        if current_scope_only:
            return None
        if self.enclosing_scope is not None:
            return self.enclosing_scope.lookup(name)
        return None
