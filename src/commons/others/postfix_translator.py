from __future__ import annotations
from src.syntactic_analysis.ast import (
    NodeBinaryArithmeticOperation,
    NodeUnaryArithmeticOperation,
    NodeNumberLiteral,
    NodeVisitor,
    NodeAST,
)


class PostfixTranslator(NodeVisitor[str]):
    __slots__ = ()

    def visit_NodeBinaryOperation(self, node: NodeBinaryArithmeticOperation) -> str:
        left_str: str = self.visit(node.left)
        right_str: str = self.visit(node.right)
        return f"{left_str} {right_str} {node.operator}"

    def visit_NodeUnaryOperation(self, node: NodeUnaryArithmeticOperation) -> str:
        operand_str: str = self.visit(node.operand)
        if node.operator == "+":
            return operand_str
        else:
            return f"{operand_str} {node.operator}"

    def visit_NodeNumber(self, node: NodeNumberLiteral) -> str:
        return node.lexeme[1:-1]

    def translate(self, tree: NodeAST) -> str:
        return self.visit(tree)
