from typing import Optional, Union
from enum import Enum


ValueType = Union[int, str, float]


class TokenType(Enum):
    PROGRAM = "PROGRAM"
    VAR = "VAR"
    PROCEDURE = "PROCEDURE"
    FUNCTION = "FUNCTION"
    INTEGER = "INTEGER"
    REAL = "REAL"
    INTEGER_CONSTANT = "INTEGER_CONSTANT"
    REAL_CONSTANT = "REAL_CONSTANT"
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
    COLON = "COLON"
    COMMA = "COMMA"
    EOF = "EOF"


class Token(object):
    __slots__ = ("type", "value")

    def __init__(self, token_type: TokenType, value: Optional[ValueType]) -> None:
        self.type: TokenType = token_type
        self.value: Optional[ValueType] = value

    def __str__(self) -> str:
        return f"({self.type.value}, {self.value!r})"

    def __repr__(self) -> str:
        return f"Token(type={self.type}, value={self.value!r})"
