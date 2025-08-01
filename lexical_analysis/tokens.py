from typing import Optional, Union
from enum import Enum


class TokenType(Enum):
    INTEGER = "INTEGER"
    FLOAT = "FLOAT"
    PLUS = "PLUS"
    MINUS = "MINUS"
    MUL = "MUL"
    TRUE_DIV = "TRUE_DIV"
    INTEGER_DIV = "INTEGER_DIV"
    MOD = "MOD"
    LEFT_PARENTHESIS = "LEFT_PARENTHESIS"
    RIGHT_PARENTHESIS = "RIGHT_PARENTHESIS"
    ID = "ID"
    BEGIN = "BEGIN"
    END = "END"
    DOT = "DOT"
    ASSIGN = "ASSIGN"
    SEMICOLON = "SEMICOLON"
    EOF = "EOF"


class Token:
    __slots__ = ("type", "value")

    def __init__(
        self, token_type: TokenType, value: Optional[Union[int, str, float]]
    ) -> None:
        self.type: TokenType = token_type
        self.value: Optional[Union[int, str, float]] = value

    def __str__(self) -> str:
        return f"({self.type.value}, {self.value!r})"

    def __repr__(self) -> str:
        return f"Token(type={self.type}, value={self.value!r})"
