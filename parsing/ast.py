from typing import Union
from abc import ABC, abstractmethod
from lexical_analysis.tokens import Token, TokenType


class NodeAST(ABC):
    __slots__ = ()

    @abstractmethod
    def __repr__(self) -> str:
        pass


class NodeEmptyStatement(NodeAST):
    __slots__ = ()

    def __repr__(self) -> str:
        return "NodeEmptyStatement()"


class NodeVariable(NodeAST):
    __slots__ = ("id",)

    def __init__(self, token: Token):
        if not token.type == TokenType.ID:
            raise TypeError(f"Invalid token type: {token.type}")
        if not isinstance(token.value, str):
            raise TypeError(f"Invalid token value type: {type(token.value).__name__}")
        self.id: str = token.value

    def __repr__(self) -> str:
        return f"NodeVariable(id={self.id})"


class NodeAssignmentStatement(NodeAST):
    __slots__ = ("left", "right")

    def __init__(self, left: NodeVariable, right: NodeAST):
        self.left: NodeVariable = left
        self.right: NodeAST = right

    def __repr__(self) -> str:
        return f"NodeAssignmentStatement(left={self.left}, right={self.right})"


class NodeCompoundStatement(NodeAST):
    __slots__ = ("children",)

    def __init__(
        self,
        children: list[
            Union["NodeCompoundStatement", NodeAssignmentStatement, NodeEmptyStatement]
        ],
    ) -> None:
        self.children: list[
            Union["NodeCompoundStatement", NodeAssignmentStatement, NodeEmptyStatement]
        ] = children

    def __repr__(self) -> str:
        return f"NodeCompoundStatement(children={str(self.children)})"


class NodeBinaryOperation(NodeAST):
    __slots__ = ("left", "right", "operator")

    def __init__(self, left: NodeAST, token: Token, right: NodeAST) -> None:
        if not isinstance(token.value, str):
            raise TypeError(f"Invalid token value type: {type(token.value).__name__}")
        self.left: NodeAST = left
        self.right: NodeAST = right
        self.operator: str = token.value

    def __repr__(self) -> str:
        return f"NodeBinaryOperation(left={self.left}, operator={self.operator}, right={self.right})"


class NodeUnaryOperation(NodeAST):
    __slots__ = ("operator", "operand")

    def __init__(self, token: Token, operand: NodeAST) -> None:
        if not isinstance(token.value, str):
            raise TypeError(f"Invalid token value type: {type(token.value).__name__}")
        self.operator: str = token.value
        self.operand: NodeAST = operand

    def __repr__(self) -> str:
        return f"NodeUnaryOperation(operator={self.operator}, operand={self.operand})"


class NodeNumber(NodeAST):
    __slots__ = ("value",)

    def __init__(self, token: Token) -> None:
        if not isinstance(token.value, (int, float)):
            raise TypeError(f"Invalid token value type: {type(token.value).__name__}")
        self.value: Union[int, float] = token.value

    def __repr__(self) -> str:
        return f"NodeNumber(value={self.value})"
