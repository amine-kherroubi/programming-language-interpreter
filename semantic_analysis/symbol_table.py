from abc import ABC, abstractmethod
from typing import Optional


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
        return f"<BUILT-IN: {self.identifier}>"


class VariableSymbol(TypedSymbol):
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(identifier='{self.identifier}', type='{self.type}')"

    def __str__(self) -> str:
        return f"<VARIABLE: {self.identifier}, {self.type}>"


class ConstantSymbol(TypedSymbol):
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(identifier='{self.identifier}', type='{self.type}')"

    def __str__(self) -> str:
        return f"<CONSTANT: {self.identifier}, {self.type}>"


from syntactic_analysis.ast import NodeBlock
from lexical_analysis.tokens import TokenType


class UnitSymbol(Symbol):
    __slots__ = ("parameters", "block", "is_anonymous")

    def __init__(
        self,
        identifier: str,
        parameters: list[VariableSymbol],
        block: NodeBlock,
        is_anonymous: bool = True,
    ) -> None:
        super().__init__(identifier)
        self.parameters: list[VariableSymbol] = parameters
        self.block: NodeBlock = block
        self.is_anonymous: bool = is_anonymous

    def make_named(self, name: str) -> None:
        self.identifier = name
        self.is_anonymous = False


class ExpressionUnitSymbol(UnitSymbol):
    __slots__ = ("return_type",)

    def __init__(
        self,
        identifier: str,
        parameters: list[VariableSymbol],
        return_type: str,
        block: NodeBlock,
        is_anonymous: bool = True,
    ) -> None:
        super().__init__(identifier, parameters, block, is_anonymous)
        self.return_type: str = return_type

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(identifier={self.identifier}, parameters={self.parameters}, return_type={self.return_type}, block={self.block}, is_anonymous={self.is_anonymous})"

    def __str__(self) -> str:
        params_str = ", ".join(
            [f"{param.identifier}: {param.type}" for param in self.parameters]
        )
        return_string = f" -> {self.return_type}" if self.return_type else ""
        anonymous_string = "(anonymous)" if self.is_anonymous else ""
        return (
            f"<UNIT: {self.identifier}({params_str}){return_string}{anonymous_string}>"
        )


class ProcedureUnitSymbol(UnitSymbol):
    __slots__ = ()

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(identifier={self.identifier}, parameters={self.parameters}, block={self.block}, is_anonymous={self.is_anonymous})"

    def __str__(self) -> str:
        params_str = ", ".join(
            [f"{param.identifier}: {param.type}" for param in self.parameters]
        )
        anonymous_string = "(anonymous)" if self.is_anonymous else ""
        return f"<UNIT: {self.identifier}({params_str}){anonymous_string}>"


class UnitHolderSymbol(TypedSymbol):
    __slots__ = ("unit_symbol", "is_constant")

    def __init__(
        self, identifier: str, unit_symbol: UnitSymbol, is_constant: bool = False
    ) -> None:
        super().__init__(identifier, TokenType.UNIT_TYPE.value)
        self.unit_symbol: UnitSymbol = unit_symbol
        self.is_constant: bool = is_constant
        unit_symbol.make_named(identifier)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(identifier='{self.identifier}', unit_symbol={self.unit_symbol}, is_constant={self.is_constant})"

    def __str__(self) -> str:
        category = "CONSTANT" if self.is_constant else "VARIABLE"
        params_string = ", ".join(
            [
                f"{param.identifier}: {param.type}"
                for param in self.unit_symbol.parameters
            ]
        )
        return_string = (
            f" -> {self.unit_symbol.return_type}"
            if isinstance(self.unit_symbol, ExpressionUnitSymbol)
            else ""
        )
        return f"<{category}-UNIT: {self.identifier}({params_string}){return_string}>"


from typing import OrderedDict


class ScopedSymbolTable:
    __slots__ = (
        "_symbols",
        "scope_name",
        "scope_level",
        "enclosing_scope",
        "_unit_counter",
    )

    BUILT_IN_TYPES: list[BuiltInTypeSymbol] = [
        BuiltInTypeSymbol(TokenType.WHOLE_TYPE.value),
        BuiltInTypeSymbol(TokenType.REAL_TYPE.value),
        BuiltInTypeSymbol(TokenType.UNIT_TYPE.value),
        BuiltInTypeSymbol(TokenType.TEXT_TYPE.value),
        BuiltInTypeSymbol(TokenType.TRUTH_TYPE.value),
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
        self._unit_counter: int = 0
        if scope_level == 1:
            self._init_builtins()

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(scope_name={self.scope_name}, scope_level={self.scope_level})"

    def __str__(self) -> str:
        return f"Symbols: {[str(value) for value in self._symbols.values()]}"

    def _init_builtins(self) -> None:
        for builtin_type in self.BUILT_IN_TYPES:
            self.define(builtin_type)

    def generate_anonymous_unit_name(self) -> str:
        self._unit_counter += 1
        return f"__anonymous_unit_{self.scope_level}_{self._unit_counter}"

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

    def lookup_callable_unit(self, name: str) -> Optional[UnitSymbol]:
        symbol = self.lookup(name)
        if isinstance(symbol, UnitSymbol):
            return symbol
        elif isinstance(symbol, UnitHolderSymbol):
            return symbol.unit_symbol
        return None
