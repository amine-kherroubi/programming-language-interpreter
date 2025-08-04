from typing import Callable, Optional, Union
import operator
from visitor_pattern.visitor import NodeVisitor
from syntactic_analysis.ast import (
    NodeAST,
    NodeBinaryOperation,
    NodeBlock,
    NodeFunctionDeclaration,
    NodeSubroutineDeclarations,
    NodeProcedureDeclaration,
    NodeVariableDeclarations,
    NodeEmpty,
    NodeAssignmentStatement,
    NodeProgram,
    NodeType,
    NodeVariable,
    NodeCompoundStatement,
    NodeNumber,
    NodeUnaryOperation,
    NodeVariableDeclaration,
)
from utils.exceptions import InterpreterError

ValueType = Union[int, float, str]
NumericType = Union[int, float]


class Interpreter(NodeVisitor[Optional[ValueType]]):
    __slots__ = ("_global_memory",)

    BINARY_OPERATORS: dict[str, Callable[[NumericType, NumericType], NumericType]] = {
        "+": operator.add,
        "-": operator.sub,
        "*": operator.mul,
        "/": operator.truediv,
        "DIV": operator.floordiv,
        "MOD": operator.mod,
    }

    UNARY_OPERATORS: dict[str, Callable[[NumericType], NumericType]] = {
        "+": operator.pos,
        "-": operator.neg,
    }

    TYPES_DEFAULT_VALUES: dict[str, ValueType] = {
        "INTEGER": 0,
        "REAL": 0.0,
    }

    def __init__(self) -> None:
        self._global_memory: dict[str, ValueType] = {}

    def __repr__(self) -> str:
        return f"Interpreter()"

    def __str__(self) -> str:
        return str(self._global_memory)

    def visit_NodeProgram(self, node: NodeProgram) -> None:
        self._global_memory["PROGRAM_NAME"] = node.program_name
        self.visit(node.main_block)

    def visit_NodeBlock(self, node: NodeBlock) -> None:
        self.visit(node.variable_declarations)
        self.visit(node.compound_statement)

    def visit_NodeVariableDeclarations(self, node: NodeVariableDeclarations) -> None:
        for declaration in node.variable_declarations:
            self.visit(declaration)

    def visit_NodeVariableDeclaration(self, node: NodeVariableDeclaration) -> None:
        node_type: str = self.visit(node.type)
        default_value: ValueType = self.TYPES_DEFAULT_VALUES[node_type]
        for variable in node.variables:
            self._global_memory[variable.id] = default_value

    def visit_NodeSubroutineDeclarations(
        self, node: NodeSubroutineDeclarations
    ) -> None:
        for declaration in node.declarations:
            self.visit(declaration)

    def visit_NodeProcedureDeclaration(self, node: NodeProcedureDeclaration) -> None:
        # SHOULDNT BE A VARIABLE SYMBOL: self._symbol_table.define(VariableSymbol(node.procedure_name, None))
        pass

    def visit_NodeFunctionDeclaration(self, node: NodeFunctionDeclaration) -> None:
        # SHOULDNT BE A VARIABLE SYMBOL: self._symbol_table.define(VariableSymbol(node.function_name, None))
        pass

    def visit_NodeType(self, node: NodeType) -> str:
        return node.type.name

    def visit_NodeEmpty(self, node: NodeEmpty) -> None:
        pass

    def visit_NodeAssignmentStatement(self, node: NodeAssignmentStatement) -> None:
        variable_name: str = node.left.id
        result: Optional[ValueType] = self.visit(node.right)
        if result is not None:
            self._global_memory[variable_name] = result

    def visit_NodeVariable(self, node: NodeVariable) -> ValueType:
        variable_name: str = node.id
        return self._global_memory[variable_name]

    def visit_NodeCompoundStatement(self, node: NodeCompoundStatement) -> None:
        for child in node.children:
            self.visit(child)

    def visit_NodeBinaryOperation(self, node: NodeBinaryOperation) -> NumericType:
        left_val: NumericType = self.visit(node.left)
        right_val: NumericType = self.visit(node.right)
        operator_symbol: str = node.operator.upper()
        if operator_symbol in ("/", "DIV", "MOD") and right_val == 0:
            raise InterpreterError("Cannot divide by zero")
        return self.BINARY_OPERATORS[operator_symbol](left_val, right_val)

    def visit_NodeUnaryOperation(self, node: NodeUnaryOperation) -> NumericType:
        operand_val: NumericType = self.visit(node.operand)
        operator_symbol: str = node.operator.upper()
        return self.UNARY_OPERATORS[operator_symbol](operand_val)

    def visit_NodeNumber(self, node: NodeNumber) -> NumericType:
        return node.value

    def interpret(self, tree: NodeAST) -> Optional[ValueType]:
        return self.visit(tree)
