from typing import Callable, NoReturn, Union
from parser import NodeAST, NodeBinaryOp, NodeUnaryOp, NodeNumber


class NodeVisitor:
    def visit(self, node: NodeAST) -> Union[int, float]:
        method_name: str = "visit_" + type(node).__name__
        visitor: Callable[[NodeAST], Union[int, float]] = getattr(
            self, method_name, self.generic_visit
        )
        return visitor(node)

    def generic_visit(self, node: NodeAST) -> NoReturn:
        raise Exception(f"No visit_{type(node).__name__} method")


class Interpreter(NodeVisitor):
    def visit_NodeNumber(self, node: NodeNumber) -> Union[int, float]:
        return node.value

    def visit_NodeBinaryOp(self, node: NodeBinaryOp) -> Union[int, float]:
        left_val = self.visit(node.left)
        right_val = self.visit(node.right)
        if node.value == "+":
            return left_val + right_val
        elif node.value == "-":
            return left_val - right_val
        elif node.value == "*":
            return left_val * right_val
        elif node.value == "/":
            if right_val == 0:
                raise Exception("Division by zero")
            return left_val / right_val
        else:
            raise Exception(f"Unknown binary operator: {node.value}")

    def visit_NodeUnaryOp(self, node: NodeUnaryOp) -> Union[int, float]:
        operand_val = self.visit(node.operand)
        if node.operator == "+":
            return +operand_val
        elif node.operator == "-":
            return -operand_val
        else:
            raise Exception(f"Unknown unary operator: {node.operator}")

    def interpret(self, tree: NodeAST) -> Union[int, float]:
        return self.visit(tree)
