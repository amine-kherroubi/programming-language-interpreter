from abc import ABC, abstractmethod
from enum import Enum
from typing import Final, Optional, OrderedDict
from _1_lexical_analysis.tokens import TokenType
from _2_syntactic_analysis.ast import NodeBlock


class Symbol(ABC):
    __slots__ = ("identifier",)

    def __init__(self, identifier: str) -> None:
        self.identifier: str = identifier

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
        self.type: str = symbol_type


class BuiltInTypeSymbol(TypelessSymbol):
    __slots__ = ()

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(identifier='{self.identifier}')"

    def __str__(self) -> str:
        return f"<BUILT-IN: {self.identifier}>"


class VariableSymbol(TypedSymbol):
    __slots__ = ()

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(identifier='{self.identifier}', type='{self.type}')"

    def __str__(self) -> str:
        return f"<VARIABLE: {self.identifier}, {self.type}>"


class ConstantSymbol(TypedSymbol):
    __slots__ = ("is_constant",)

    def __init__(self, identifier: str, symbol_type: str) -> None:
        super().__init__(identifier, symbol_type)
        self.is_constant: bool = True

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(identifier='{self.identifier}', type='{self.type}')"

    def __str__(self) -> str:
        return f"<CONSTANT: {self.identifier}, {self.type}>"


class FunctionSymbol(Symbol):
    __slots__ = ("parameters", "give_type", "block")

    def __init__(
        self,
        identifier: str,
        parameters: Optional[list[VariableSymbol]],
        give_type: str,
        block: NodeBlock,
    ) -> None:
        super().__init__(identifier)
        self.parameters: Optional[list[VariableSymbol]] = parameters
        self.give_type: str = give_type
        self.block: NodeBlock = block

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(identifier='{self.identifier}', parameters={self.parameters}, give_type='{self.give_type}')"

    def __str__(self) -> str:
        params: str = (
            ", ".join(f"{p.identifier}: {p.type}" for p in self.parameters)
            if self.parameters
            else ""
        )
        return f"<FUNCTION: {self.identifier}({params}) -> {self.give_type}>"


class ProcedureSymbol(Symbol):
    __slots__ = ("parameters", "block")

    def __init__(
        self,
        identifier: str,
        parameters: Optional[list[VariableSymbol]],
        block: NodeBlock,
    ) -> None:
        super().__init__(identifier)
        self.parameters: Optional[list[VariableSymbol]] = parameters
        self.block: NodeBlock = block

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(identifier='{self.identifier}', parameters={self.parameters})"

    def __str__(self) -> str:
        params: str = (
            ", ".join(f"{p.identifier}: {p.type}" for p in self.parameters)
            if self.parameters
            else ""
        )
        return f"<PROCEDURE: {self.identifier}({params})>"


class ScopeType(Enum):
    PROGRAM = "PROGRAM"
    FUNCTION = "FUNCTION"
    PROCEDURE = "PROCEDURE"
    IF_BLOCK = "IF_BLOCK"
    ELIF_BLOCK = "ELIF_BLOCK"
    ELSE_BLOCK = "ELSE_BLOCK"
    WHILE_BLOCK = "WHILE_BLOCK"


class ScopedSymbolTable:
    __slots__ = (
        "_symbols",
        "name",
        "type",
        "level",
        "enclosing_scope",
    )

    BUILT_IN_TYPES: Final[list[BuiltInTypeSymbol]] = [
        BuiltInTypeSymbol(TokenType.NUMBER_TYPE.value),
        BuiltInTypeSymbol(TokenType.STRING_TYPE.value),
        BuiltInTypeSymbol(TokenType.BOOLEAN_TYPE.value),
    ]

    def __init__(
        self,
        name: str,
        type: ScopeType,
        level: int,
        enclosing_scope: Optional["ScopedSymbolTable"],
    ) -> None:
        self.name: str = name
        self.type: ScopeType = type
        self.level: int = level
        self.enclosing_scope: Optional[ScopedSymbolTable] = enclosing_scope
        self._symbols: OrderedDict[str, Symbol] = OrderedDict()

        if level == 1:
            self._init_builtins()

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}(name='{self.name}', type={self.type}, "
            f"level={self.level}, enclosing_scope={self.enclosing_scope})"
        )

    def __str__(self) -> str:
        symbols: str = ", ".join(str(symbol) for symbol in self._symbols.values())
        return f"Scope '{self.name}' (level {self.level}): [{symbols}]"

    def _init_builtins(self) -> None:
        for builtin in self.BUILT_IN_TYPES:
            self.define(builtin)

    def define(self, symbol: Symbol) -> None:
        self._symbols[symbol.identifier] = symbol

    def lookup(self, name: str, current_scope_only: bool = False) -> Optional[Symbol]:
        symbol: Optional[Symbol] = self._symbols.get(name)
        if symbol:
            return symbol
        if not current_scope_only and self.enclosing_scope:
            return self.enclosing_scope.lookup(name)
        return None
