from visitor_pattern.visitor import NodeVisitor
from syntactic_analysis.ast import (
    NodeAST,
    NodeAssignmentStatement,
    NodeBinaryOperation,
    NodeBlock,
    NodeCompoundStatement,
    NodeFunctionDeclaration,
    NodeSubroutineDeclarations,
    NodeProcedureDeclaration,
    NodeVariableDeclarations,
    NodeEmpty,
    NodeNumber,
    NodeUnaryOperation,
    NodeVariable,
    NodeVariableDeclarationGroup,
    NodeProgram,
)
from semantic_analysis.symbol_table import (
    ScopedSymbolTable,
    VariableSymbol,
    ProgramSymbol,
    ProcedureSymbol,
    FunctionSymbol,
)
from utils.exceptions import SemanticAnalyzerError


class SemanticAnalyzer(NodeVisitor[None]):
    __slots__ = ("_current_scope",)

    def __init__(self) -> None:
        self._current_scope: ScopedSymbolTable = ScopedSymbolTable("External", 0, None)

    def __repr__(self) -> str:
        return "SemanticAnalyzer()"

    def __str__(self) -> str:
        return str(self._current_scope)

    def visit_NodeProgram(self, node: NodeProgram) -> None:
        self._current_scope.define(ProgramSymbol(node.name))
        program_scope: ScopedSymbolTable = ScopedSymbolTable(
            "Global", 1, self._current_scope
        )
        self._current_scope = program_scope
        self.visit(node.block)
        self._current_scope = self._current_scope.enclosing_scope

    def visit_NodeBlock(self, node: NodeBlock) -> None:
        self.visit(node.variable_declarations)
        self.visit(node.subroutine_declarations)
        self.visit(node.compound_statement)

    def visit_NodeVariableDeclarations(self, node: NodeVariableDeclarations) -> None:
        for declaration in node.variable_declarations:
            self.visit(declaration)

    def visit_NodeVariableDeclarationGroup(
        self, node: NodeVariableDeclarationGroup
    ) -> None:
        type_name: str = node.type.name
        for variable in node.members:
            if self._current_scope.lookup(variable_name := variable.name) is None:
                self._current_scope.define(VariableSymbol(variable_name, type_name))
            else:
                raise SemanticAnalyzerError(
                    f"Duplicate declaration for variable {variable_name}"
                )

    def visit_NodeCompoundStatement(self, node: NodeCompoundStatement) -> None:
        for child in node.children:
            self.visit(child)

    def visit_NodeAssignmentStatement(self, node: NodeAssignmentStatement) -> None:
        self.visit(node.left)
        self.visit(node.right)

    def visit_NodeEmpty(self, node: NodeEmpty) -> None:
        pass

    def visit_NodeVariable(self, node: NodeVariable) -> None:
        if self._current_scope.lookup(variable_name := node.name) is None:
            raise SemanticAnalyzerError(f"Undeclared variable {variable_name}")

    def visit_NodeNumber(self, node: NodeNumber) -> None:
        pass

    def visit_NodeBinaryOperation(self, node: NodeBinaryOperation) -> None:
        self.visit(node.left)
        self.visit(node.right)

    def visit_NodeUnaryOperation(self, node: NodeUnaryOperation) -> None:
        self.visit(node.operand)

    def visit_NodeSubroutineDeclarations(
        self, node: NodeSubroutineDeclarations
    ) -> None:
        for declaration in node.declarations:
            self.visit(declaration)

    def visit_NodeProcedureDeclaration(self, node: NodeProcedureDeclaration) -> None:
        parameters: list[VariableSymbol] = []
        if not isinstance(node.parameters, NodeEmpty):
            for parameter_group in node.parameters:
                parameters.extend(
                    [
                        VariableSymbol(member.name, parameter_group.type.name)
                        for member in parameter_group.members
                    ]
                )
        procedure_symbol: ProcedureSymbol = ProcedureSymbol(node.name, parameters)
        self._current_scope.define(procedure_symbol)
        procedure_scope: ScopedSymbolTable = ScopedSymbolTable(
            scope_name=node.name,
            scope_level=self._current_scope.scope_level + 1,
            enclosing_scope=self._current_scope,
        )
        for param in parameters:
            procedure_scope.define(param)
        previous_scope: ScopedSymbolTable = self._current_scope
        self._current_scope = procedure_scope
        self.visit(node.block)
        self._current_scope = previous_scope

    def visit_NodeFunctionDeclaration(self, node: NodeFunctionDeclaration) -> None:
        parameters: list[VariableSymbol] = []
        if not isinstance(node.parameters, NodeEmpty):
            for parameter_group in node.parameters:
                parameters.extend(
                    [
                        VariableSymbol(variable.name, parameter_group.type.name)
                        for variable in parameter_group.members
                    ]
                )
        function_symbol: FunctionSymbol = FunctionSymbol(
            node.name, parameters, node.type.name
        )
        self._current_scope.define(function_symbol)
        function_scope: ScopedSymbolTable = ScopedSymbolTable(
            scope_name=node.name,
            scope_level=self._current_scope.scope_level + 1,
            enclosing_scope=self._current_scope,
        )
        for param in parameters:
            function_scope.define(param)
        previous_scope: ScopedSymbolTable = self._current_scope
        self._current_scope = function_scope
        self.visit(node.block)
        self._current_scope = previous_scope

    def analyze(self, tree: NodeAST) -> None:
        self.visit(tree)
