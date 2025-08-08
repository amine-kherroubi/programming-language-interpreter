from visitor_pattern.visitor import NodeVisitor
from syntactic_analysis.ast import (
    NodeAST,
    NodeAssignmentStatement,
    NodeBinaryOperation,
    NodeBlock,
    NodeConstantDeclaration,
    NodeGiveStatement,
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
    UnitHolderSymbol,
    ScopedSymbolTable,
    UnitSymbol,
    VariableSymbol,
)
from utils.error_handling import SemanticError, ErrorCode
from lexical_analysis.tokens import TokenType


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
        if node.expression_group is not None:
            for identifier, expression in zip(
                node.identifier_group, node.expression_group
            ):
                if (
                    isinstance(expression, NodeUnit)
                    and node.type.name == TokenType.UNIT_TYPE.value
                ):
                    unit_symbol = self._create_unit_symbol_from_node(expression)
                    unit_holder = UnitHolderSymbol(
                        identifier.name, unit_symbol, is_constant=False
                    )
                    self._current_scope.define(unit_holder)
                else:
                    self._current_scope.define(
                        VariableSymbol(identifier.name, node.type.name)
                    )
                    self.visit(expression)
        else:
            for member in node.identifier_group:
                self._current_scope.define(VariableSymbol(member.name, node.type.name))

    def visit_NodeConstantDeclaration(self, node: NodeConstantDeclaration) -> None:
        for same_type_group in node.same_type_groups:
            self.visit(same_type_group)

    def visit_NodeSameTypeConstantDeclarationGroup(
        self, node: NodeSameTypeConstantDeclarationGroup
    ) -> None:
        for identifier, expression in zip(node.identifier_group, node.expression_group):
            if (
                isinstance(expression, NodeUnit)
                and node.type.name == TokenType.UNIT_TYPE.value
            ):
                unit_symbol = self._create_unit_symbol_from_node(expression)
                unit_holder = UnitHolderSymbol(
                    identifier.name, unit_symbol, is_constant=True
                )
                self._current_scope.define(unit_holder)
            else:
                self._current_scope.define(
                    ConstantSymbol(identifier.name, node.type.name)
                )
                self.visit(expression)

    def visit_NodeAssignmentStatement(self, node: NodeAssignmentStatement) -> None:
        symbol = self._current_scope.lookup(node.identifier.name)
        if symbol is None:
            raise SemanticError(
                ErrorCode.UNDECLARED_IDENTIFIER,
                f"Undeclared variable {node.identifier.name}",
            )
        if isinstance(symbol, (ConstantSymbol, UnitHolderSymbol)) and getattr(
            symbol, "is_constant", True
        ):
            raise SemanticError(
                ErrorCode.ASSIGNMENT_TO_CONSTANT,
                f"Cannot assign to constant {node.identifier.name}",
            )
        if isinstance(node.expression, NodeUnit):
            if not (
                isinstance(symbol, VariableSymbol)
                and symbol.type == TokenType.UNIT_TYPE.value
            ):
                raise SemanticError(
                    ErrorCode.TYPE_MISMATCH,
                    f"Cannot assign unit to non-unit variable {node.identifier.name}",
                )
            unit_symbol = self._create_unit_symbol_from_node(node.expression)
            unit_holder = UnitHolderSymbol(
                node.identifier.name, unit_symbol, is_constant=False
            )
            self._current_scope.define(unit_holder)
        else:
            self.visit(node.expression)

    def visit_NodeIdentifier(self, node: NodeIdentifier) -> None:
        if self._current_scope.lookup(node.name) is None:
            raise SemanticError(
                ErrorCode.UNDECLARED_IDENTIFIER, f"Undeclared identifier {node.name}"
            )

    def visit_NodeNumericLiteral(self, node: NodeNumericLiteral) -> None:
        pass

    def visit_NodeBinaryOperation(self, node: NodeBinaryOperation) -> None:
        self.visit(node.left_expression)
        self.visit(node.right_expression)

    def visit_NodeUnaryOperation(self, node: NodeUnaryOperation) -> None:
        self.visit(node.expression)

    def visit_NodeUnit(self, node: NodeUnit) -> None:
        unit_symbol = self._create_unit_symbol_from_node(node)
        anonymous_name = self._current_scope.generate_anonymous_unit_name()
        unit_symbol.identifier = anonymous_name
        self._current_scope.define(unit_symbol)
        self._enter_unit_scope(unit_symbol)
        self.visit(node.block)
        self._exit_scope()

    def visit_NodeUnitUse(self, node: NodeUnitUse) -> None:
        unit_symbol = self._current_scope.lookup_callable_unit(node.identifier.name)
        if unit_symbol is None:
            symbol = self._current_scope.lookup(node.identifier.name)
            if symbol is None:
                raise SemanticError(
                    ErrorCode.UNDECLARED_IDENTIFIER,
                    f"Undeclared identifier {node.identifier.name}",
                )
            else:
                raise SemanticError(
                    ErrorCode.WRONG_SYMBOL_TYPE, f"{node.identifier.name} is not a unit"
                )
        expected_args = len(unit_symbol.parameters) if unit_symbol.parameters else 0
        actual_args = len(node.arguments) if node.arguments else 0
        if expected_args != actual_args:
            raise SemanticError(
                ErrorCode.WRONG_NUMBER_OF_ARGUMENTS,
                f"Unit {node.identifier.name} expects {expected_args} arguments, got {actual_args}",
            )
        node.symbol = unit_symbol
        if node.arguments:
            for argument in node.arguments:
                self.visit(argument)

    def visit_NodeGiveStatement(self, node: NodeGiveStatement) -> None:
        pass

    def _create_unit_symbol_from_node(self, node: NodeUnit) -> UnitSymbol:
        parameters: list[VariableSymbol] = []
        if node.parameters:
            for parameter in node.parameters:
                parameters.append(
                    VariableSymbol(parameter.identifier.name, parameter.type.name)
                )
        return_type = node.return_type.name if node.return_type else None
        return UnitSymbol(
            identifier="__temp__",
            parameters=parameters,
            return_type=return_type,
            block=node.block,
            is_anonymous=True,
        )

    def _enter_unit_scope(self, unit_symbol: UnitSymbol) -> None:
        unit_scope = ScopedSymbolTable(
            scope_name=unit_symbol.identifier,
            scope_level=self._current_scope.scope_level + 1,
            enclosing_scope=self._current_scope,
        )
        for parameter in unit_symbol.parameters:
            unit_scope.define(parameter)
        self._current_scope = unit_scope

    def _exit_scope(self) -> None:
        if self._current_scope.enclosing_scope is not None:
            self._current_scope = self._current_scope.enclosing_scope

    def _check_unit_return_type(self, node: NodeUnit) -> None:
        for statement in node.block.statements:
            if (
                isinstance(statement, NodeGiveStatement)
                and statement.expression is not None
            ):
                break
        else:
            if node.return_type is not None:
                raise SemanticError(
                    ErrorCode.PROCEDURE_UNIT_RETURNING_VALUE,
                    "Procedure unit should not return a value",
                )
        if node.return_type is not None:
            raise SemanticError(
                ErrorCode.EXPRESSION_UNIT_NOT_RETURNING_VALUE,
                "Expression unit should always return a value",
            )

    def analyze(self, tree: NodeAST) -> None:
        self.visit(tree)
