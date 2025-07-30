from typing import Callable, Union
import operator
from interpreting.visitor import NodeVisitor
from parsing.ast import NodeAST, NodeBinaryOp, NodeNumber, NodeUnaryOp
from util.exceptions import InterpreterError


class Interpreter(NodeVisitor[Union[int, float]]):
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

    def visit_NodeNumber(self, node: NodeNumber) -> Union[int, float]:
        return node.value

    def visit_NodeBinaryOp(self, node: NodeBinaryOp) -> Union[int, float]:
        left_val = self.visit(node.left)
        right_val = self.visit(node.right)
        if node.operator == "/" and right_val == 0:
            raise ZeroDivisionError("Cannot divide by zero")
        if node.operator in self.BINARY_OPERATORS:
            return self.BINARY_OPERATORS[node.operator](left_val, right_val)
        else:
            raise InterpreterError(f"Unknown binary operator: {node.operator}")

    def visit_NodeUnaryOp(self, node: NodeUnaryOp) -> Union[int, float]:
        operand_val = self.visit(node.operand)

        if node.operator in self.UNARY_OPERATORS:
            return self.UNARY_OPERATORS[node.operator](operand_val)
        else:
            raise InterpreterError(f"Unknown unary operator: {node.operator}")

    def interpret(self, tree: NodeAST) -> Union[int, float]:
        return self.visit(tree)
