# semantic_analyzer.py

from typing import Optional

from visitor_pattern.visitor import NodeVisitor
from syntactic_analysis.ast import (
    NodeAST,
    NodeProgram,
    NodeBlock,
    NodeStatement,
    NodeExpression,
    NodeVariableDeclaration,
    NodeConstantDeclaration,
    NodeAssignment,
    NodeFunctionDeclaration,
    NodeProcedureDeclaration,
    NodeFunctionCall,
    NodeProcedureCall,
    NodeGiveStatement,
    NodeIdentifier,
    NodeBinaryOperation,
    NodeUnaryOperation,
    NodeIntegerLiteral,
    NodeFloatLiteral,
    NodeStringLiteral,
    NodeBooleanLiteral,
)
from semantic_analysis.symbol_table import (
    ScopedSymbolTable,
    VariableSymbol,
    ConstantSymbol,
    FunctionSymbol,
    ProcedureSymbol,
)
from utils.error_handling import SemanticError, ErrorCode


class SemanticAnalyzer(NodeVisitor[None]):
    __slots__ = ("_current_scope", "_current_function")

    def __init__(self) -> None:
        self._current_scope = ScopedSymbolTable("global", 1, None)
        self._current_function: Optional[str] = None

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
        for i, identifier in enumerate(node.identifiers):
            self._ensure_not_redeclared(identifier.name, "Variable")

            symbol = VariableSymbol(identifier.name, node.type.name)
            self._current_scope.define(symbol)

            if node.expressions and i < len(node.expressions):
                self.visit(node.expressions[i])

    def visit_NodeConstantDeclaration(self, node: NodeConstantDeclaration) -> None:
        for i, identifier in enumerate(node.identifiers):
            self._ensure_not_redeclared(identifier.name, "Constant")

            symbol = ConstantSymbol(identifier.name, node.type.name)
            self._current_scope.define(symbol)

            self.visit(node.expressions[i])

    def visit_NodeFunctionDeclaration(self, node: NodeFunctionDeclaration) -> None:
        name = node.name.name
        self._ensure_not_redeclared(name, "Function")

        params = [
            VariableSymbol(param.identifier.name, param.type.name)
            for param in node.parameters or []
        ]

        self._current_scope.define(
            FunctionSymbol(name, params, node.return_type.name, node.block)
        )

        self._enter_function_scope(name, params)
        previous_function = self._current_function
        self._current_function = name

        self.visit(node.block)

        self._current_function = previous_function
        self._exit_scope()

    def visit_NodeProcedureDeclaration(self, node: NodeProcedureDeclaration) -> None:
        name = node.name.name
        self._ensure_not_redeclared(name, "Procedure")

        params = [
            VariableSymbol(param.identifier.name, param.type.name)
            for param in node.parameters or []
        ]

        self._current_scope.define(ProcedureSymbol(name, params, node.block))

        self._enter_function_scope(name, params)
        previous_function = self._current_function
        self._current_function = name

        self.visit(node.block)

        self._current_function = previous_function
        self._exit_scope()

    def visit_NodeAssignment(self, node: NodeAssignment) -> None:
        symbol = self._current_scope.lookup(node.identifier.name)
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
        symbol = self._current_scope.lookup_callable(node.name.name)
        if symbol is None:
            raise SemanticError(
                ErrorCode.UNDECLARED_IDENTIFIER,
                f"Undeclared function '{node.name.name}'",
            )
        if not isinstance(symbol, FunctionSymbol):
            raise SemanticError(
                ErrorCode.WRONG_SYMBOL_TYPE,
                f"'{node.name.name}' is not a function",
            )

        self._check_argument_count(node.name.name, symbol.parameters, node.arguments)
        for arg in node.arguments or []:
            self.visit(arg)

    def visit_NodeProcedureCall(self, node: NodeProcedureCall) -> None:
        symbol = self._current_scope.lookup_callable(node.name.name)
        if symbol is None:
            raise SemanticError(
                ErrorCode.UNDECLARED_IDENTIFIER,
                f"Undeclared procedure '{node.name.name}'",
            )
        if not isinstance(symbol, ProcedureSymbol):
            raise SemanticError(
                ErrorCode.WRONG_SYMBOL_TYPE,
                f"'{node.name.name}' is not a procedure",
            )

        self._check_argument_count(node.name.name, symbol.parameters, node.arguments)
        for arg in node.arguments or []:
            self.visit(arg)

    def visit_NodeGiveStatement(self, node: NodeGiveStatement) -> None:
        if not self._current_function:
            raise SemanticError(
                ErrorCode.WRONG_SYMBOL_TYPE,
                "Give statement outside of function or procedure",
            )

        function_symbol = self._current_scope.enclosing_scope.lookup(
            self._current_function
        )

        if isinstance(function_symbol, FunctionSymbol):
            if node.expression is None:
                raise SemanticError(
                    ErrorCode.EXPRESSION_UNIT_EMPTY_RETURN,
                    f"Function '{self._current_function}' must return a value",
                )
            self.visit(node.expression)

        elif isinstance(function_symbol, ProcedureSymbol):
            if node.expression is not None:
                raise SemanticError(
                    ErrorCode.PROCEDURE_UNIT_RETURNING_VALUE,
                    f"Procedure '{self._current_function}' cannot return a value",
                )

    def visit_NodeIdentifier(self, node: NodeIdentifier) -> None:
        if self._current_scope.lookup(node.name) is None:
            raise SemanticError(
                ErrorCode.UNDECLARED_IDENTIFIER,
                f"Undeclared identifier '{node.name}'",
            )

    def visit_NodeBinaryOperation(self, node: NodeBinaryOperation) -> None:
        self.visit(node.left)
        self.visit(node.right)

    def visit_NodeUnaryOperation(self, node: NodeUnaryOperation) -> None:
        self.visit(node.operand)

    def visit_NodeIntegerLiteral(self, node: NodeIntegerLiteral) -> None:
        pass

    def visit_NodeFloatLiteral(self, node: NodeFloatLiteral) -> None:
        pass

    def visit_NodeStringLiteral(self, node: NodeStringLiteral) -> None:
        pass

    def visit_NodeBooleanLiteral(self, node: NodeBooleanLiteral) -> None:
        pass

    # -- Helpers --

    def _enter_function_scope(self, name: str, params: list[VariableSymbol]) -> None:
        new_scope = ScopedSymbolTable(
            name, self._current_scope.scope_level + 1, self._current_scope
        )
        for param in params:
            new_scope.define(param)
        self._current_scope = new_scope

    def _exit_scope(self) -> None:
        if self._current_scope.enclosing_scope:
            self._current_scope = self._current_scope.enclosing_scope

    def _ensure_not_redeclared(self, name: str, kind: str) -> None:
        if self._current_scope.lookup(name, current_scope_only=True):
            raise SemanticError(
                ErrorCode.DUPLICATE_IDENTIFIER,
                f"{kind} '{name}' already declared in this scope",
            )

    def _check_argument_count(
        self,
        name: str,
        parameters: Optional[list[VariableSymbol]],
        arguments: Optional[list[NodeExpression]],
    ) -> None:
        expected = len(parameters) if parameters else 0
        actual = len(arguments) if arguments else 0
        if expected != actual:
            raise SemanticError(
                ErrorCode.WRONG_NUMBER_OF_ARGUMENTS,
                f"'{name}' expects {expected} arguments, got {actual}",
            )
