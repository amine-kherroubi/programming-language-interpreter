from typing import Union
from abc import ABC, abstractmethod
from lexical_analysis.tokens import Token, TokenType


class NodeAST(ABC):
    __slots__ = ()

    @abstractmethod
    def __repr__(self) -> str:
        pass


class NodeNoOp(NodeAST):
    __slots__ = ()

    def __repr__(self) -> str:
        return "NodeNoOp()"


class NodeVar(NodeAST):
    __slots__ = "id"

    def __init__(self, token: Token):
        if not token.type == TokenType.ID:
            raise TypeError(f"Invalid token type: {token.type}")
        if not isinstance(token.value, str):
            raise TypeError(f"Invalid token value type: {type(token.value).__name__}")
        self.id: str = token.value

    def __repr__(self) -> str:
        return f"NodeVar(id={self.id})"


class NodeAssign(NodeAST):
    __slots__ = ("left", "right")

    def __init__(self, left: NodeVar, right: NodeAST):
        self.left: NodeVar = left
        self.right: NodeAST = right

    def __repr__(self) -> str:
        return f"NodeAssign(left={self.left}, right={self.right})"


class NodeCompoundStatement(NodeAST):
    __slots__ = "children"

    def __init__(
        self, children: list[Union["NodeCompoundStatement", NodeAssign, NodeNoOp]]
    ) -> None:
        self.children: list[Union["NodeCompoundStatement", NodeAssign, NodeNoOp]] = (
            children
        )

    def __repr__(self) -> str:
        return f"NodeCompoundStatement(children={str(self.children)})"


class NodeBinaryOp(NodeAST):
    __slots__ = ("left", "right", "operator")

    def __init__(self, left: NodeAST, token: Token, right: NodeAST) -> None:
        if not isinstance(token.value, str):
            raise TypeError(f"Invalid token value type: {type(token.value).__name__}")
        self.left: NodeAST = left
        self.right: NodeAST = right
        self.operator: str = token.value

    def __repr__(self) -> str:
        return f"NodeBinaryOp(left={self.left}, operator={self.operator}, right={self.right})"


class NodeUnaryOp(NodeAST):
    __slots__ = ("operator", "operand")

    def __init__(self, token: Token, operand: NodeAST) -> None:
        if not isinstance(token.value, str):
            raise TypeError(f"Invalid token value type: {type(token.value).__name__}")
        self.operator: str = token.value
        self.operand: NodeAST = operand

    def __repr__(self) -> str:
        return f"NodeUnaryOp(operator={self.operator}, operand={self.operand})"


class NodeNumber(NodeAST):
    __slots__ = "value"

    def __init__(self, token: Token) -> None:
        if not isinstance(token.value, (int, float)):
            raise TypeError(f"Invalid token value type: {type(token.value).__name__}")
        self.value: Union[int, float] = token.value

    def __repr__(self) -> str:
        return f"NodeNumber(value={self.value})"
