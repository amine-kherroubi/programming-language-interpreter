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
    DIV = "DIV"
    MOD = "MOD"
    BEGIN = "BEGIN"
    END = "END"
    PLUS = "+"
    MINUS = "-"
    MUL = "*"
    TRUE_DIV = "/"
    LEFT_PARENTHESIS = "("
    RIGHT_PARENTHESIS = ")"
    SEMICOLON = ";"
    COLON = ":"
    COMMA = ","
    DOT = "."
    INTEGER_CONSTANT = "INTEGER_CONSTANT"
    REAL_CONSTANT = "REAL_CONSTANT"
    ASSIGN = "ASSIGN"
    ID = "ID"
    EOF = "EOF"


class Token(object):
    __slots__ = ("type", "value", "line", "column")

    def __init__(
        self, token_type: TokenType, value: Optional[ValueType], line: int, column: int
    ) -> None:
        self.type: TokenType = token_type
        self.value: Optional[ValueType] = value
        self.line: int = line
        self.column: int = column

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(type={self.type}, value={self.value!r}, line={self.line}, column={self.column})"

    def __str__(self) -> str:
        return f"({self.type.value}, {self.value!r})[line={self.line}, column={self.column}]"
