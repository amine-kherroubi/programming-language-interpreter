from typing import Union
from parser import NodeAST, NodeBinaryOp, NodeUnaryOp, NodeNumber


class Interpreter:
    def evaluate(self, node: NodeAST) -> Union[int, float]:
        if isinstance(node, NodeNumber):
            return node.value

        elif isinstance(node, NodeBinaryOp):
            left_val = self.evaluate(node.left)
            right_val = self.evaluate(node.right)

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

        elif isinstance(node, NodeUnaryOp):
            operand_val = self.evaluate(node.operand)

            if node.operator == "+":
                return +operand_val
            elif node.operator == "-":
                return -operand_val
            else:
                raise Exception(f"Unknown unary operator: {node.operator}")

        else:
            raise Exception(f"Unknown node type: {type(node).__name__}")

    def interpret(self, tree: NodeAST) -> Union[int, float]:
        return self.evaluate(tree)
