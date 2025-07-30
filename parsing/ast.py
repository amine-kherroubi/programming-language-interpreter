from typing import Union
from abc import ABC, abstractmethod

from lexical_analysis.tokens import Token


class NodeAST(ABC):
    __slots__ = ()

    @abstractmethod
    def __str__(self) -> str:
        pass


class NodeBinaryOp(NodeAST):
    __slots__ = ("left", "right", "operator")

    def __init__(self, left: NodeAST, token: Token, right: NodeAST) -> None:
        if not isinstance(token.value, str):
            raise TypeError(f"Invalid token value type: {type(token.value).__name__}")
        self.left: NodeAST = left
        self.right: NodeAST = right
        self.operator: str = token.value

    def __str__(self) -> str:
        return f"({self.left} {self.operator} {self.right})"


class NodeUnaryOp(NodeAST):
    __slots__ = ("operator", "operand")

    def __init__(self, token: Token, operand: NodeAST) -> None:
        if not isinstance(token.value, str):
            raise TypeError(f"Invalid token value type: {type(token.value).__name__}")
        self.operator: str = token.value
        self.operand: NodeAST = operand

    def __str__(self) -> str:
        return f"({self.operator}{self.operand})"


class NodeNumber(NodeAST):
    __slots__ = ("value",)

    def __init__(self, token: Token) -> None:
        if not isinstance(token.value, (int, float)):
            raise TypeError(f"Invalid token value type: {type(token.value).__name__}")
        self.value: Union[int, float] = token.value

    def __str__(self) -> str:
        return str(self.value)
