from typing import Callable, Optional, Union
import operator
from interpreting.visitor import NodeVisitor
from parsing.ast import (
    NodeAST,
    NodeBinaryOperation,
    NodeEmptyStatement,
    NodeAssignmentStatement,
    NodeVariable,
    NodeCompoundStatement,
    NodeNumber,
    NodeUnaryOperation,
)
from utils.exceptions import InterpreterError


class Interpreter(NodeVisitor[Optional[Union[int, float]]]):
    __slots__ = ("symbol_table",)

    def __init__(self) -> None:
        self.symbol_table: dict[str, Union[int, float]] = {}

    BINARY_OPERATORS: dict[
        str, Callable[[Union[int, float], Union[int, float]], Union[int, float]]
    ] = {
        "+": operator.add,
        "-": operator.sub,
        "*": operator.mul,
        "/": operator.truediv,
    }

    UNARY_OPERATORS: dict[str, Callable[[Union[int, float]], Union[int, float]]] = {
        "+": operator.pos,
        "-": operator.neg,
    }

    def visit_NodeEmptyStatement(self, node: NodeEmptyStatement) -> None:
        pass

    def visit_NodeAssignmentStatement(self, node: NodeAssignmentStatement) -> None:
        result: Optional[Union[int, float]] = self.visit(node.right)
        if result is not None:
            self.symbol_table[node.left.id] = result

    def visit_NodeVariable(self, node: NodeVariable) -> Union[int, float]:
        variable_name: str = node.id
        variable_value: Optional[Union[int, float]] = self.symbol_table.get(
            variable_name
        )
        if variable_value is None:
            raise NameError(f"Variable '{variable_name}' is not defined")
        else:
            return variable_value

    def visit_NodeCompoundStatement(self, node: NodeCompoundStatement) -> None:
        child: Union[NodeCompoundStatement, NodeAssignmentStatement, NodeEmptyStatement]
        for child in node.children:
            self.visit(child)

    def visit_NodeBinaryOperation(self, node: NodeBinaryOperation) -> Union[int, float]:
        left_val: Optional[Union[int, float]] = self.visit(node.left)
        right_val: Optional[Union[int, float]] = self.visit(node.right)
        if left_val is None or right_val is None:
            raise InterpreterError("Expression evaluation returned None")
        if node.operator == "/" and right_val == 0:
            raise ZeroDivisionError("Cannot divide by zero")
        if node.operator in self.BINARY_OPERATORS:
            return self.BINARY_OPERATORS[node.operator](left_val, right_val)
        else:
            raise InterpreterError(f"Unknown binary operator: {node.operator}")

    def visit_NodeUnaryOperation(self, node: NodeUnaryOperation) -> Union[int, float]:
        operand_val: Optional[Union[int, float]] = self.visit(node.operand)
        if operand_val is None:
            raise InterpreterError("Expression evaluation returned None")
        if node.operator in self.UNARY_OPERATORS:
            return self.UNARY_OPERATORS[node.operator](operand_val)
        else:
            raise InterpreterError(f"Unknown unary operator: {node.operator}")

    def visit_NodeNumber(self, node: NodeNumber) -> Union[int, float]:
        return node.value

    def interpret(self, tree: NodeAST) -> Optional[Union[int, float]]:
        return self.visit(tree)
