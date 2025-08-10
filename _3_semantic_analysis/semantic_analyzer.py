from typing import Optional
from utils.visitor import NodeVisitor
from _2_syntactic_analysis.ast import (
    NodeAST,
    NodeArithmeticExpressionAsBoolean,
    NodeBinaryBooleanOperation,
    NodeComparisonExpression,
    NodeElif,
    NodeElse,
    NodeIfStatement,
    NodeProgram,
    NodeBlock,
    NodeShowStatement,
    NodeSkipStatement,
    NodeStopStatement,
    NodeUnaryBooleanOperation,
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
    NodeWhileStatement,
)
from _3_semantic_analysis.symbol_table import (
    ScopedSymbolTable,
    Symbol,
    VariableSymbol,
    ConstantSymbol,
    FunctionSymbol,
    ProcedureSymbol,
    ScopeType,
)
from utils.errors import SemanticError, ErrorCode


class SemanticAnalyzer(NodeVisitor[None]):
    __slots__ = "_current_scope"

    def __init__(self) -> None:
        self._current_scope: ScopedSymbolTable = ScopedSymbolTable(
            "global", ScopeType.PROGRAM, 1, None
        )

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}()"

    def __str__(self) -> str:
        return str(self._current_scope)

    def analyze(self, tree: NodeAST) -> None:
        self.visit(tree)

    def visit_NodeProgram(self, node: NodeProgram) -> None:
        self.visit(node.block)

    def visit_NodeBlock(self, node: NodeBlock) -> None:
        for statement in node.statements or []:
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

        self._enter_scope(name, ScopeType.FUNCTION, parameters)
        self.visit(node.block)
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

        self._enter_scope(name, ScopeType.PROCEDURE, parameters)
        self.visit(node.block)
        self._exit_scope()

    def visit_NodeAssignmentStatement(self, node: NodeAssignmentStatement) -> None:
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
        if self._current_scope.type not in (ScopeType.FUNCTION, ScopeType.PROCEDURE):
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
            self._current_scope.enclosing_scope.lookup(self._current_scope.name)
        )

        if isinstance(subroutine_symbol, FunctionSymbol):
            if node.expression is None:
                raise SemanticError(
                    ErrorCode.FUNCTION_EMPTY_GIVE,
                    f"Function '{self._current_scope.name}' must give a value",
                )
            self.visit(node.expression)

        elif isinstance(subroutine_symbol, ProcedureSymbol):
            if node.expression is not None:
                raise SemanticError(
                    ErrorCode.PROCEDURE_GIVING_VALUE,
                    f"Procedure '{self._current_scope.name}' cannot give a value",
                )

    def visit_NodeShowStatement(self, node: NodeShowStatement) -> None:
        self.visit(node.expression)

    def visit_NodeIfStatement(self, node: NodeIfStatement) -> None:
        self.visit(node.condition)
        self._enter_scope(
            f"if_statement_{self._current_scope.level}",
            ScopeType.IF_BLOCK,
            None,
        )
        self.visit(node.block)
        self._exit_scope()
        for elif_ in node.elifs or []:
            self.visit(elif_)
        if node.else_:
            self.visit(node.else_)

    def visit_NodeElif(self, node: NodeElif) -> None:
        self.visit(node.condition)
        self._enter_scope(
            f"elif_statement_{self._current_scope.level}",
            ScopeType.ELIF_BLOCK,
            None,
        )
        self.visit(node.block)
        self._exit_scope()

    def visit_NodeElse(self, node: NodeElse) -> None:
        self._enter_scope(
            f"else_statement_{self._current_scope.level}",
            ScopeType.ELSE_BLOCK,
            None,
        )
        self.visit(node.block)
        self._exit_scope()

    def visit_NodeWhileStatement(self, node: NodeWhileStatement):
        self.visit(node.condition)
        self._enter_scope(
            f"while_statement_{self._current_scope.level}", ScopeType.WHILE_BLOCK, None
        )
        self.visit(node.block)
        self._exit_scope()

    def visit_NodeSkipStatement(self, node: NodeSkipStatement) -> None:
        scope: Optional[ScopedSymbolTable] = self._current_scope
        while scope is not None:
            if scope.type == ScopeType.WHILE_BLOCK:
                return
            scope = scope.enclosing_scope
        raise SemanticError(
            ErrorCode.SKIP_STATEMENT_OUTSIDE_WHILE,
            "skip statements can only be used inside while blocks",
        )

    def visit_NodeStopStatement(self, node: NodeStopStatement) -> None:
        scope: Optional[ScopedSymbolTable] = self._current_scope
        while scope is not None:
            if scope.type == ScopeType.WHILE_BLOCK:
                return
            scope = scope.enclosing_scope
        raise SemanticError(
            ErrorCode.STOP_STATEMENT_OUTSIDE_WHILE,
            "stop statements can only be used inside while blocks",
        )

    def visit_NodeIdentifier(self, node: NodeIdentifier) -> None:
        if self._current_scope.lookup(node.name) is None:
            raise SemanticError(
                ErrorCode.UNDECLARED_IDENTIFIER,
                f"Undeclared identifier '{node.name}'",
            )

    def visit_NodeArithmeticExpressionAsBoolean(
        self, node: NodeArithmeticExpressionAsBoolean
    ) -> None:
        self.visit(node.expression)

    def visit_NodeBinaryArithmeticOperation(
        self, node: NodeBinaryArithmeticOperation
    ) -> None:
        self.visit(node.left)
        self.visit(node.right)

    def visit_NodeUnaryArithmeticOperation(
        self, node: NodeUnaryArithmeticOperation
    ) -> None:
        self.visit(node.operand)

    def visit_NodeBinaryBooleanOperation(
        self, node: NodeBinaryBooleanOperation
    ) -> None:
        self.visit(node.left)
        self.visit(node.right)

    def visit_NodeUnaryBooleanOperation(self, node: NodeUnaryBooleanOperation) -> None:
        self.visit(node.operand)

    def visit_NodeComparisonExpression(self, node: NodeComparisonExpression) -> None:
        self.visit(node.left)
        self.visit(node.right)

    def visit_NodeIntegerLiteral(self, node: NodeIntegerLiteral) -> None:
        pass

    def visit_NodeFloatLiteral(self, node: NodeFloatLiteral) -> None:
        pass

    def visit_NodeStringLiteral(self, node: NodeStringLiteral) -> None:
        pass

    def visit_NodeBooleanLiteral(self, node: NodeBooleanLiteral) -> None:
        pass

    def _enter_scope(
        self,
        name: str,
        type: ScopeType,
        variable_symbols: Optional[list[VariableSymbol]],
    ) -> None:
        new_scope: ScopedSymbolTable = ScopedSymbolTable(
            name, type, self._current_scope.level + 1, self._current_scope
        )
        for variable_symbol in variable_symbols or []:
            new_scope.define(variable_symbol)
        self._current_scope = new_scope

    def _exit_scope(self) -> None:
        if self._current_scope.enclosing_scope:
            self._current_scope = self._current_scope.enclosing_scope
