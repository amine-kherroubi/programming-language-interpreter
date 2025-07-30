from typing import Union, NoReturn
from lexer import Lexer
from tokens import (
    Token,
    INTEGER,
    FLOAT,
    PLUS,
    MINUS,
    MUL,
    DIV,
    LEFT_PARENTHESIS,
    RIGHT_PARENTHESIS,
)


class NodeAST:
    __slots__ = ()
    pass


class NodeBinaryOp(NodeAST):
    __slots__ = (
        "left",
        "right",
        "value",
    )

    def __init__(self, left: NodeAST, token: Token, right: NodeAST) -> None:
        if not isinstance(token.value, str):
            raise TypeError(f"Invalid token value type: {type(token.value).__name__}")
        self.left: NodeAST = left
        self.right: NodeAST = right
        self.value: str = token.value


class NodeUnaryOp(NodeAST):
    __slots__ = (
        "operator",
        "operand",
    )

    def __init__(self, token: Token, operand: NodeAST) -> None:
        if not isinstance(token.value, str):
            raise TypeError(f"Invalid token value type: {type(token.value).__name__}")
        self.operator: str = token.value
        self.operand: NodeAST = operand


class NodeNumber(NodeAST):
    __slots__ = ("value",)

    def __init__(self, token: Token) -> None:
        if not isinstance(token.value, (int, float)):
            raise TypeError(f"Invalid token value type: {type(token.value).__name__}")
        self.value: Union[int, float] = token.value


class Parser:
    __slots__ = (
        "lexer",
        "current_token",
    )

    def __init__(self, lexer: Lexer) -> None:
        self.lexer: Lexer = lexer
        self.current_token: Token = self.lexer.next_token()

    def error(self) -> NoReturn:
        raise Exception("Invalid syntax")

    def consume(self, token_type: str) -> None:
        if self.current_token.type == token_type:
            self.current_token = self.lexer.next_token()
        else:
            self.error()

    def factor(self) -> NodeAST:
        token: Token = self.current_token
        if token.type == INTEGER:
            self.consume(INTEGER)
            return NodeNumber(token)
        elif token.type == FLOAT:
            self.consume(FLOAT)
            return NodeNumber(token)
        elif token.type == LEFT_PARENTHESIS:
            self.consume(LEFT_PARENTHESIS)
            node = self.expression()
            self.consume(RIGHT_PARENTHESIS)
            return node
        elif token.type == PLUS:
            self.consume(PLUS)
            node = self.factor()
            return NodeUnaryOp(token, node)
        elif token.type == MINUS:
            self.consume(MINUS)
            node = self.factor()
            return NodeUnaryOp(token, node)
        self.error()

    def term(self) -> NodeAST:
        node = self.factor()
        while self.current_token.type in (MUL, DIV):
            token = self.current_token
            if token.type == MUL:
                self.consume(MUL)
            elif token.type == DIV:
                self.consume(DIV)
            node = NodeBinaryOp(left=node, token=token, right=self.factor())
        return node

    def expression(self) -> NodeAST:
        node = self.term()
        while self.current_token.type in (PLUS, MINUS):
            token = self.current_token
            if token.type == PLUS:
                self.consume(PLUS)
            elif token.type == MINUS:
                self.consume(MINUS)
            node = NodeBinaryOp(left=node, token=token, right=self.term())
        return node

    def parse(self) -> NodeAST:
        return self.expression()
