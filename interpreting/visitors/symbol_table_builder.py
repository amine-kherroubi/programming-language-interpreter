from interpreting.symbols import SymbolTable_, VariableSymbol
from interpreting.visitor import NodeVisitor
from parsing.ast import (
    NodeAST,
    NodeAssignmentStatement,
    NodeBinaryOperation,
    NodeBlock,
    NodeCompoundStatement,
    NodeVariableDeclarations,
    NodeEmpty,
    NodeNumber,
    NodeUnaryOperation,
    NodeVariable,
    NodeVariableDeclaration,
    NodeProgram,
)
from utils.exceptions import SymbolTableError


class SymbolTableBuilder(NodeVisitor[None]):
    __slots__ = ()

    def __init__(self, symbol_table: SymbolTable_) -> None:
        self._symbol_table: SymbolTable_ = symbol_table

    def visit_NodeProgram(self, node: NodeProgram) -> None:
        self.visit(node.main_block)

    def visit_NodeBlock(self, node: NodeBlock) -> None:
        self.visit(node.variable_declarations)
        self.visit(node.compound_statement)

    def visit_NodeVariableDeclarations(self, node: NodeVariableDeclarations) -> None:
        for declaration in node.variable_declarations:
            self.visit(declaration)

    def visit_NodeVariableDeclaration(self, node: NodeVariableDeclaration) -> None:
        type: str = node.type.type.name
        for variable in node.variables:
            self._symbol_table.define(VariableSymbol(variable.id, type))

    def visit_NodeCompoundStatement(self, node: NodeCompoundStatement) -> None:
        for child in node.children:
            self.visit(child)

    def visit_NodeAssignmentStatement(self, node: NodeAssignmentStatement) -> None:
        self.visit(node.left)
        self.visit(node.right)

    def visit_NodeEmpty(self, node: NodeEmpty) -> None:
        pass

    def visit_NodeVariable(self, node: NodeVariable) -> None:
        if self._symbol_table.lookup(variable_name := node.id) is None:
            raise SymbolTableError(f"Undeclared variable: {variable_name}")

    def visit_NodeNumber(self, node: NodeNumber) -> None:
        pass

    def visit_NodeBinaryOperation(self, node: NodeBinaryOperation) -> None:
        self.visit(node.left)
        self.visit(node.right)

    def visit_NodeUnaryOperation(self, node: NodeUnaryOperation) -> None:
        self.visit(node.operand)

    def build(self, tree: NodeAST) -> None:
        self.visit(tree)
