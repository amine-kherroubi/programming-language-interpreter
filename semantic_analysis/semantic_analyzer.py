from typing import Optional
from visitor_pattern.visitor import NodeVisitor
from syntactic_analysis.ast import (
    NodeAST,
    NodeAssignmentStatement,
    NodeBinaryOperation,
    NodeBlock,
    NodeConstantDeclaration,
    NodeIdentifier,
    NodeNumericLiteral,
    NodeProgram,
    NodeSameTypeConstantDeclarationGroup,
    NodeSameTypeVariableDeclarationGroup,
    NodeUnaryOperation,
    NodeUnit,
    NodeUnitUse,
    NodeVariableDeclaration,
)
from semantic_analysis.symbol_table import (
    ConstantSymbol,
    ScopedSymbolTable,
    Symbol,
    UnitSymbol,
    VariableSymbol,
)
from utils.error_handling import SemanticError, ErrorCode


class SemanticAnalyzer(NodeVisitor[None]):
    __slots__ = ("_current_scope",)

    def __init__(self) -> None:
        self._current_scope: ScopedSymbolTable = ScopedSymbolTable("Global", 1, None)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}()"

    def __str__(self) -> str:
        return str(self._current_scope)

    def visit_NodeProgram(self, node: NodeProgram) -> None:
        self.visit(node.block)

    def visit_NodeBlock(self, node: NodeBlock) -> None:
        for statement in node.statements:
            self.visit(statement)

    def visit_NodeVariableDeclaration(self, node: NodeVariableDeclaration) -> None:
        for same_type_group in node.same_type_groups:
            self.visit(same_type_group)

    def visit_NodeSameTypeVariableDeclarationGroup(
        self, node: NodeSameTypeVariableDeclarationGroup
    ) -> None:
        for member in node.identifier_group:
            self._current_scope.define(VariableSymbol(member.name, node.type.name))

    def visit_NodeConstantDeclaration(self, node: NodeConstantDeclaration) -> None:
        for same_type_group in node.same_type_groups:
            self.visit(same_type_group)

    def visit_NodeSameTypeConstantDeclarationGroup(
        self, node: NodeSameTypeConstantDeclarationGroup
    ) -> None:
        for member in node.identifier_group:
            self._current_scope.define(ConstantSymbol(member.name, node.type.name))

    def visit_NodeAssignmentStatement(self, node: NodeAssignmentStatement) -> None:
        self.visit(node.identifier)
        self.visit(node.expression)

    def visit_NodeIdentifier(self, node: NodeIdentifier) -> None:
        if self._current_scope.lookup(id := node.name) is None:
            raise SemanticError(
                ErrorCode.UNDECLARED_IDENTIFIER, f"Undeclared variable {id}"
            )

    def visit_NodeNumber(self, node: NodeNumericLiteral) -> None:
        pass

    def visit_NodeBinaryOperation(self, node: NodeBinaryOperation) -> None:
        self.visit(node.left_expression)
        self.visit(node.right_expression)

    def visit_NodeUnaryOperation(self, node: NodeUnaryOperation) -> None:
        self.visit(node.expression)

    def visit_NodeUnit(self, node: NodeUnit) -> None:
        parameters: list[VariableSymbol] = []
        if node.parameters is not None:
            for parameter in node.parameters:
                parameters.append(
                    VariableSymbol(parameter.identifier.name, parameter.type.name)
                )
        gives_type: Optional[str] = node.type.name if node.type is not None else None
        unit_symbol: UnitSymbol = UnitSymbol(
            "anonymous", parameters, gives_type, node.block
        )
        self._current_scope.define(unit_symbol)
        unit_scope: ScopedSymbolTable = ScopedSymbolTable(
            scope_name="anonymous",
            scope_level=self._current_scope.scope_level + 1,
            enclosing_scope=self._current_scope,
        )
        for parameter in parameters:
            unit_scope.define(parameter)
        self._current_scope = unit_scope
        self.visit(node.block)
        self._current_scope = unit_scope.enclosing_scope

    def visit_NodeUnitUse(self, node: NodeUnitUse) -> None:
        unit_symbol: Optional[Symbol] = self._current_scope.lookup(node.identifier.name)
        if unit_symbol is None:
            raise SemanticError(
                ErrorCode.UNDECLARED_IDENTIFIER,
                f"Undeclared unit {node.identifier.name}",
            )
        if not isinstance(unit_symbol, UnitSymbol):
            raise SemanticError(
                ErrorCode.WRONG_SYMBOL_TYPE, f"{node.identifier.name} is not a unit"
            )
        if node.arguments is None:
            if len(unit_symbol.parameters) > 0:
                raise SemanticError(
                    ErrorCode.WRONG_NUMBER_OF_ARGUMENTS,
                    f"Function {node.identifier.name} expects {len(unit_symbol.parameters)} arguments, got 0",
                )
            return
        if (expected_args := len(unit_symbol.parameters)) != (
            actual_args := len(node.arguments)
        ):
            raise SemanticError(
                ErrorCode.WRONG_NUMBER_OF_ARGUMENTS,
                f"Function {node.identifier.name} expects {expected_args} arguments, got {actual_args}",
            )
        node.symbol = unit_symbol
        for argument in node.arguments:
            self.visit(argument)

    def analyze(self, tree: NodeAST) -> None:
        self.visit(tree)
