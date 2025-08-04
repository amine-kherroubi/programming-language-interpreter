from visitor_pattern.visitor import NodeVisitor
from syntactic_analysis.ast import (
    NodeAST,
    NodeBinaryOperation,
    NodeNumber,
    NodeUnaryOperation,
)


class PrefixTranslator(NodeVisitor[str]):
    __slots__ = ()

    def visit_NodeBinaryOperation(self, node: NodeBinaryOperation) -> str:
        left_str: str = self.visit(node.left)
        right_str: str = self.visit(node.right)
        return f"({node.operator} {left_str} {right_str})"

    def visit_NodeUnaryOperation(self, node: NodeUnaryOperation) -> str:
        operand_str: str = self.visit(node.operand)
        if node.operator == "+":
            return operand_str
        else:
            return f"({node.operator} {operand_str})"

    def visit_NodeNumber(self, node: NodeNumber) -> str:
        return str(node.value)

    def translate(self, tree: NodeAST) -> str:
        return self.visit(tree)
