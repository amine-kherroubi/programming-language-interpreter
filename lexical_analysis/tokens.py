from typing import Optional, Union
from enum import Enum

ValueType = Union[int, str, float, bool]


class TokenType(Enum):
    LEFT_BRACE = "{"
    RIGHT_BRACE = "}"
    LEFT_PARENTHESIS = "("
    RIGHT_PARENTHESIS = ")"
    LEFT_BRACKET = "["
    RIGHT_BRACKET = "]"
    COMMA = ","
    COLON = ":"
    SEMICOLON = ";"
    ASSIGN = "="
    PLUS = "+"
    MINUS = "-"
    MULTIPLY = "*"
    DIVIDE = "/"
    MODULO = "%"
    ARROW = "->"
    FLOOR_DIVIDE = "//"
    POWER = "**"
    LET = "let"
    KEEP = "keep"
    GIVE = "give"
    WHOLE_TYPE = "whole"
    REAL_TYPE = "real"
    TEXT_TYPE = "text"
    TRUTH_TYPE = "truth"
    UNIT_TYPE = "unit"
    WHOLE_LITERAL = "WHOLE_LITERAL"
    REAL_LITERAL = "REAL_LITERAL"
    TEXT_LITERAL = "TEXT_LITERAL"
    TRUTH_LITERAL = "TRUTH_LITERAL"
    IDENTIFIER = "IDENTIFIER"
    NEWLINE = "NEWLINE"
    EOF = "EOF"


class Token:
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
