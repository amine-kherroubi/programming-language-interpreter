from interpreting.visitor import NodeVisitor
from parsing.ast import NodeAST, NodeBinaryOperation, NodeNumber, NodeUnaryOperation


class PostfixTranslator(NodeVisitor[str]):
    __slots__ = ()

    def visit_NodeBinaryOperation(self, node: NodeBinaryOperation) -> str:
        left_str = self.visit(node.left)
        right_str = self.visit(node.right)
        return f"{left_str} {right_str} {node.operator}"

    def visit_NodeUnaryOperation(self, node: NodeUnaryOperation) -> str:
        operand_str = self.visit(node.operand)
        if node.operator == "+":
            return operand_str
        else:
            return f"{operand_str} {node.operator}"

    def visit_NodeNumber(self, node: NodeNumber) -> str:
        return str(node.value)

    def translate(self, tree: NodeAST) -> str:
        return self.visit(tree)
