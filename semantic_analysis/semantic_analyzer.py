from typing import Optional

from visitor_pattern.visitor import NodeVisitor
from syntactic_analysis.ast import (
    NodeAST,
    NodeProgram,
    NodeBlock,
    NodeVariableDeclaration,
    NodeConstantDeclaration,
    NodeAssignmentStatement,
    NodeFunctionDeclaration,
    NodeProcedureDeclaration,
    NodeFunctionCall,
    NodeProcedureCall,
    NodeGiveStatement,
    NodeIdentifier,
    NodeBinaryArithmeticOperation,
    NodeUnaryArithmeticOperation,
    NodeIntegerLiteral,
    NodeFloatLiteral,
    NodeStringLiteral,
    NodeBooleanLiteral,
)
from semantic_analysis.symbol_table import (
    ScopedSymbolTable,
    Symbol,
    VariableSymbol,
    ConstantSymbol,
    FunctionSymbol,
    ProcedureSymbol,
)
from utils.error_handling import SemanticError, ErrorCode


class SemanticAnalyzer(NodeVisitor[None]):
    __slots__ = ("_current_scope", "_current_subroutine")

    def __init__(self) -> None:
        self._current_scope: ScopedSymbolTable = ScopedSymbolTable("global", 1, None)
        self._current_subroutine: Optional[str] = None

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}()"

    def __str__(self) -> str:
        return str(self._current_scope)

    def analyze(self, tree: NodeAST) -> None:
        self.visit(tree)

    def visit_NodeProgram(self, node: NodeProgram) -> None:
        self.visit(node.block)

    def visit_NodeBlock(self, node: NodeBlock) -> None:
        for statement in node.statements:
            self.visit(statement)

    def visit_NodeVariableDeclaration(self, node: NodeVariableDeclaration) -> None:
        for index, identifier in enumerate(node.identifiers):
            if self._current_scope.lookup(identifier.name, current_scope_only=True):
                raise SemanticError(
                    ErrorCode.DUPLICATE_IDENTIFIER,
                    f"Variable '{identifier.name}' already declared in this scope",
                )

            symbol: VariableSymbol = VariableSymbol(identifier.name, node.type.name)
            self._current_scope.define(symbol)

            if node.expressions and index < len(node.expressions):
                self.visit(node.expressions[index])

    def visit_NodeConstantDeclaration(self, node: NodeConstantDeclaration) -> None:
        for index, identifier in enumerate(node.identifiers):
            if self._current_scope.lookup(identifier.name, current_scope_only=True):
                raise SemanticError(
                    ErrorCode.DUPLICATE_IDENTIFIER,
                    f"Constant '{identifier.name}' already declared in this scope",
                )

            symbol: ConstantSymbol = ConstantSymbol(identifier.name, node.type.name)
            self._current_scope.define(symbol)

            self.visit(node.expressions[index])

    def visit_NodeFunctionDeclaration(self, node: NodeFunctionDeclaration) -> None:
        name: str = node.identifier.name
        if self._current_scope.lookup(name, current_scope_only=True):
            raise SemanticError(
                ErrorCode.DUPLICATE_IDENTIFIER,
                f"Function '{name}' already declared in this scope",
            )

        parameters: list[VariableSymbol] = [
            VariableSymbol(parameter.identifier.name, parameter.type.name)
            for parameter in (node.parameters or [])
        ]

        self._current_scope.define(
            FunctionSymbol(
                name,
                parameters if parameters else None,
                node.give_type.name,
                node.block,
            )
        )

        self._enter_subroutine_scope(name, parameters)
        previous_subroutine: Optional[str] = self._current_subroutine
        self._current_subroutine = name

        self.visit(node.block)

        self._current_subroutine = previous_subroutine
        self._exit_scope()

    def visit_NodeProcedureDeclaration(self, node: NodeProcedureDeclaration) -> None:
        name: str = node.identifier.name
        if self._current_scope.lookup(name, current_scope_only=True):
            raise SemanticError(
                ErrorCode.DUPLICATE_IDENTIFIER,
                f"Procedure '{name}' already declared in this scope",
            )

        parameters: list[VariableSymbol] = [
            VariableSymbol(parameter.identifier.name, parameter.type.name)
            for parameter in (node.parameters or [])
        ]

        self._current_scope.define(
            ProcedureSymbol(name, parameters if parameters else None, node.block)
        )

        self._enter_subroutine_scope(name, parameters)
        previous_subroutine: Optional[str] = self._current_subroutine
        self._current_subroutine = name

        self.visit(node.block)

        self._current_subroutine = previous_subroutine
        self._exit_scope()

    def visit_NodeAssignment(self, node: NodeAssignmentStatement) -> None:
        symbol: Optional[Symbol] = self._current_scope.lookup(node.identifier.name)
        if symbol is None:
            raise SemanticError(
                ErrorCode.UNDECLARED_IDENTIFIER,
                f"Undeclared variable '{node.identifier.name}'",
            )
        if isinstance(symbol, ConstantSymbol):
            raise SemanticError(
                ErrorCode.ASSIGNMENT_TO_CONSTANT,
                f"Cannot assign to constant '{node.identifier.name}'",
            )
        if not isinstance(symbol, VariableSymbol):
            raise SemanticError(
                ErrorCode.WRONG_SYMBOL_TYPE,
                f"'{node.identifier.name}' is not a variable",
            )

        self.visit(node.expression)

    def visit_NodeFunctionCall(self, node: NodeFunctionCall) -> None:
        symbol: Optional[Symbol] = self._current_scope.lookup(node.identifier.name)
        if symbol is None:
            raise SemanticError(
                ErrorCode.UNDECLARED_IDENTIFIER,
                f"Undeclared function '{node.identifier.name}'",
            )
        if not isinstance(symbol, FunctionSymbol):
            raise SemanticError(
                ErrorCode.WRONG_SYMBOL_TYPE,
                f"'{node.identifier.name}' is not a function",
            )

        expected_arguments_count: int = (
            len(symbol.parameters) if symbol.parameters else 0
        )
        actual_arguments_count: int = len(node.arguments) if node.arguments else 0
        if expected_arguments_count != actual_arguments_count:
            raise SemanticError(
                ErrorCode.WRONG_NUMBER_OF_ARGUMENTS,
                f"'{node.identifier.name}' expects {expected_arguments_count} arguments, got {actual_arguments_count}",
            )
        for argument in node.arguments or []:
            self.visit(argument)

    def visit_NodeProcedureCall(self, node: NodeProcedureCall) -> None:
        symbol: Optional[Symbol] = self._current_scope.lookup(node.identifier.name)
        if symbol is None:
            raise SemanticError(
                ErrorCode.UNDECLARED_IDENTIFIER,
                f"Undeclared procedure '{node.identifier.name}'",
            )
        if not isinstance(symbol, ProcedureSymbol):
            raise SemanticError(
                ErrorCode.WRONG_SYMBOL_TYPE,
                f"'{node.identifier.name}' is not a procedure",
            )

        expected_arguments_count: int = (
            len(symbol.parameters) if symbol.parameters else 0
        )
        actual_arguments_count: int = len(node.arguments) if node.arguments else 0
        if expected_arguments_count != actual_arguments_count:
            raise SemanticError(
                ErrorCode.WRONG_NUMBER_OF_ARGUMENTS,
                f"'{node.identifier.name}' expects {expected_arguments_count} arguments, got {actual_arguments_count}",
            )
        for argument in node.arguments or []:
            self.visit(argument)

    def visit_NodeGiveStatement(self, node: NodeGiveStatement) -> None:
        if not self._current_subroutine:
            raise SemanticError(
                ErrorCode.WRONG_SYMBOL_TYPE,
                "Give statement outside of function or procedure",
            )

        if not self._current_scope.enclosing_scope:
            raise SemanticError(
                ErrorCode.WRONG_SYMBOL_TYPE,
                "Invalid scope structure",
            )

        subroutine_symbol: Optional[Symbol] = (
            self._current_scope.enclosing_scope.lookup(self._current_subroutine)
        )

        if isinstance(subroutine_symbol, FunctionSymbol):
            if node.expression is None:
                raise SemanticError(
                    ErrorCode.FUNCTION_EMPTY_GIVE,
                    f"Function '{self._current_subroutine}' must give a value",
                )
            self.visit(node.expression)

        elif isinstance(subroutine_symbol, ProcedureSymbol):
            if node.expression is not None:
                raise SemanticError(
                    ErrorCode.PROCEDURE_GIVING_VALUE,
                    f"Procedure '{self._current_subroutine}' cannot give a value",
                )

    def visit_NodeIdentifier(self, node: NodeIdentifier) -> None:
        if self._current_scope.lookup(node.name) is None:
            raise SemanticError(
                ErrorCode.UNDECLARED_IDENTIFIER,
                f"Undeclared identifier '{node.name}'",
            )

    def visit_NodeBinaryOperation(self, node: NodeBinaryArithmeticOperation) -> None:
        self.visit(node.left)
        self.visit(node.right)

    def visit_NodeUnaryOperation(self, node: NodeUnaryArithmeticOperation) -> None:
        self.visit(node.operand)

    def visit_NodeIntegerLiteral(self, node: NodeIntegerLiteral) -> None:
        pass

    def visit_NodeFloatLiteral(self, node: NodeFloatLiteral) -> None:
        pass

    def visit_NodeStringLiteral(self, node: NodeStringLiteral) -> None:
        pass

    def visit_NodeBooleanLiteral(self, node: NodeBooleanLiteral) -> None:
        pass

    def _enter_subroutine_scope(
        self, name: str, parameters: list[VariableSymbol]
    ) -> None:
        new_scope: ScopedSymbolTable = ScopedSymbolTable(
            name, self._current_scope.scope_level + 1, self._current_scope
        )
        for parameter in parameters:
            new_scope.define(parameter)
        self._current_scope = new_scope

    def _exit_scope(self) -> None:
        if self._current_scope.enclosing_scope:
            self._current_scope = self._current_scope.enclosing_scope
