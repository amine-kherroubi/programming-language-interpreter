from typing import Callable, Optional, Union
import operator
from interpreting.visitor import NodeVisitor
from parsing.ast import (
    NodeAST,
    NodeBinaryOperation,
    NodeDeclarations,
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


class Interpreter(NodeVisitor[Optional[Union[int, float, str]]]):
    __slots__ = ("symbol_table",)

    def __init__(self) -> None:
        self.symbol_table: dict[str, Union[int, float, str]] = {}

    BINARY_OPERATORS: dict[
        str, Callable[[Union[int, float], Union[int, float]], Union[int, float]]
    ] = {
        "+": operator.add,
        "-": operator.sub,
        "*": operator.mul,
        "/": operator.truediv,
        "DIV": operator.floordiv,
        "MOD": operator.mod,
    }

    UNARY_OPERATORS: dict[str, Callable[[Union[int, float]], Union[int, float]]] = {
        "+": operator.pos,
        "-": operator.neg,
    }

    TYPES_DEFAULT_VALUES: dict[str, Union[int, float, str]] = {
        "INTEGER_TYPE": 0,
        "REAL_TYPE": 0.0,
    }

    def visit_NodeProgram(self, node: NodeProgram) -> None:
        self.symbol_table[node.program_name] = node.program_name
        self.visit(node.variable_declaration_section)
        self.visit(node.main_block)

    def visit_NodeDeclarations(self, node: NodeDeclarations) -> None:
        for declaration in node.declarations:
            self.visit(declaration)

    def visit_NodeVariableDeclaration(self, node: NodeVariableDeclaration) -> None:
        for variable in node.variables:
            type = self.visit(node.type)
            if not isinstance(type, str):
                raise InterpreterError("Type evaluation did not return a string")
            self.symbol_table[variable.id] = self.TYPES_DEFAULT_VALUES[type]

    def visit_NodeType(self, node: NodeType) -> str:
        return node.type.name

    def visit_NodeEmpty(self, node: NodeEmpty) -> None:
        pass

    def visit_NodeAssignmentStatement(self, node: NodeAssignmentStatement) -> None:
        result: Optional[Union[int, float, str]] = self.visit(node.right)
        if result is not None:
            self.symbol_table[node.left.id] = result

    def visit_NodeVariable(self, node: NodeVariable) -> Union[int, float, str]:
        variable_name: str = node.id
        variable_value: Optional[Union[int, float, str]] = self.symbol_table.get(
            variable_name
        )
        if variable_value is None:
            raise NameError(f"Variable '{variable_name}' is not defined")
        else:
            return variable_value

    def visit_NodeCompoundStatement(self, node: NodeCompoundStatement) -> None:
        for child in node.children:
            self.visit(child)

    def visit_NodeBinaryOperation(self, node: NodeBinaryOperation) -> Union[int, float]:
        left_val: Optional[Union[int, float, str]] = self.visit(node.left)
        right_val: Optional[Union[int, float, str]] = self.visit(node.right)
        if not isinstance(left_val, (int, float)) or not isinstance(
            right_val, (int, float)
        ):
            raise InterpreterError("Expression evaluation returned wrong type")
        op = node.operator.upper()
        if op in ("/", "DIV", "MOD") and right_val == 0:
            raise ZeroDivisionError("Cannot divide by zero")
        if op in self.BINARY_OPERATORS:
            return self.BINARY_OPERATORS[op](left_val, right_val)
        else:
            raise InterpreterError(f"Unknown binary operator: {op}")

    def visit_NodeUnaryOperation(self, node: NodeUnaryOperation) -> Union[int, float]:
        operand_val: Optional[Union[int, float, str]] = self.visit(node.operand)
        if not isinstance(operand_val, (int, float)):
            raise InterpreterError("Expression evaluation returned wrong type")
        op = node.operator.upper()
        if op in self.UNARY_OPERATORS:
            return self.UNARY_OPERATORS[op](operand_val)
        else:
            raise InterpreterError(f"Unknown unary operator: {op}")

    def visit_NodeNumber(self, node: NodeNumber) -> Union[int, float]:
        return node.value

    def interpret(self, tree: NodeAST) -> Optional[Union[int, float, str]]:
        return self.visit(tree)
