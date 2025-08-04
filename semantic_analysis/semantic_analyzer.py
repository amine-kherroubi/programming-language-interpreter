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
    SymbolTable_,
    VariableSymbol,
    ProgramSymbol,
    ProcedureSymbol,
    FunctionSymbol,
)
from utils.exceptions import SemanticAnalyzerError


class SemanticAnalyzer(NodeVisitor[None]):
    __slots__ = ("_symbol_table",)

    def __init__(self, symbol_table: SymbolTable_) -> None:
        self._symbol_table: SymbolTable_ = symbol_table

    def __repr__(self) -> str:
        return f"SemanticAnalyzer(_symbol_table={self._symbol_table!r})"

    def __str__(self) -> str:
        return str(self._symbol_table)

    def visit_NodeProgram(self, node: NodeProgram) -> None:
        self._symbol_table.define(ProgramSymbol(node.name))
        self.visit(node.block)

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
        type: str = node.type.name
        for variable in node.members:
            if not self._symbol_table.lookup(variable_name := variable.name):
                self._symbol_table.define(VariableSymbol(variable_name, type))
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
        if self._symbol_table.lookup(variable_name := node.name) is None:
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
                parameters += [
                    VariableSymbol(member.name, parameter_group.type.name)
                    for member in parameter_group.members
                ]
        self._symbol_table.define(ProcedureSymbol(node.name, parameters))
        self.visit(node.block)

    def visit_NodeFunctionDeclaration(self, node: NodeFunctionDeclaration) -> None:
        parameters: list[VariableSymbol] = []
        if not isinstance(node.parameters, NodeEmpty):
            for parameter_group in node.parameters:
                parameters += [
                    VariableSymbol(variable.name, parameter_group.type.name)
                    for variable in parameter_group.members
                ]
        self._symbol_table.define(FunctionSymbol(node.name, parameters, node.type.name))
        self.visit(node.block)

    def build(self, tree: NodeAST) -> None:
        self.visit(tree)
