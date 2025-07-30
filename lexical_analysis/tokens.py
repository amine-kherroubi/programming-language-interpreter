from typing import Union
from enum import Enum


class TokenType(Enum):
    INTEGER = "INTEGER"
    FLOAT = "FLOAT"
    PLUS = "PLUS"
    MINUS = "MINUS"
    MUL = "MUL"
    DIV = "DIV"
    LEFT_PARENTHESIS = "LEFT_PARENTHESIS"
    RIGHT_PARENTHESIS = "RIGHT_PARENTHESIS"
    EOF = "EOF"


class Token:
    __slots__ = ("type", "value")

    def __init__(self, token_type: TokenType, value: Union[int, str, float]) -> None:
        self.type: TokenType = token_type
        self.value: Union[int, str, float] = value

    def __str__(self) -> str:
        return f"({self.type.value}, {self.value!r})"

    def __repr__(self) -> str:
        return f"Token(type={self.type}, value={self.value!r})"
