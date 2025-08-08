from enum import Enum
from typing import Optional, Union


ValueType = Union[int, str, float, bool]


class TokenType(Enum):
    # Single-character tokens
    LEFT_BRACE = "{"
    RIGHT_BRACE = "}"
    LEFT_PARENTHESIS = "("
    RIGHT_PARENTHESIS = ")"
    COMMA = ","
    COLON = ":"
    ASSIGN = "="
    PLUS = "+"
    MINUS = "-"
    MULTIPLY = "*"
    DIVIDE = "/"
    MODULO = "%"

    # Multi-character operators
    FLOOR_DIVIDE = "//"
    POWER = "**"
    ARROW = "->"

    # Keywords
    LET = "let"
    KEEP = "keep"
    GIVE = "give"
    FUNC = "func"
    PROC = "proc"
    EXEC = "exec"

    # Types
    INT_TYPE = "int"
    FLOAT_TYPE = "float"
    STRING_TYPE = "string"
    BOOL_TYPE = "bool"

    # Literals and structure
    INT_LITERAL = "INT_LITERAL"
    FLOAT_LITERAL = "FLOAT_LITERAL"
    STRING_LITERAL = "STRING_LITERAL"
    BOOL_LITERAL = "BOOL_LITERAL"
    IDENTIFIER = "IDENTIFIER"
    NEWLINE = "NEWLINE"
    EOF = "EOF"


# Mapping of reserved keywords to token types
RESERVED_KEYWORDS: dict[str, TokenType] = {
    "let": TokenType.LET,
    "keep": TokenType.KEEP,
    "give": TokenType.GIVE,
    "func": TokenType.FUNC,
    "proc": TokenType.PROC,
    "exec": TokenType.EXEC,
    "int": TokenType.INT_TYPE,
    "float": TokenType.FLOAT_TYPE,
    "string": TokenType.STRING_TYPE,
    "bool": TokenType.BOOL_TYPE,
}

# Mapping of single-character symbols to token types
SINGLE_CHARACTER_TOKEN_TYPES: dict[str, TokenType] = {
    "{": TokenType.LEFT_BRACE,
    "}": TokenType.RIGHT_BRACE,
    "(": TokenType.LEFT_PARENTHESIS,
    ")": TokenType.RIGHT_PARENTHESIS,
    ",": TokenType.COMMA,
    ":": TokenType.COLON,
    "=": TokenType.ASSIGN,
    "+": TokenType.PLUS,
    "-": TokenType.MINUS,
    "*": TokenType.MULTIPLY,
    "/": TokenType.DIVIDE,
    "%": TokenType.MODULO,
}

# Multi-character operators
MULTI_CHAR_OPERATORS: dict[str, TokenType] = {
    "->": TokenType.ARROW,
    "**": TokenType.POWER,
    "//": TokenType.FLOOR_DIVIDE,
}


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
        return (
            f"{self.__class__.__name__}(type={self.type}, value={self.value!r}, "
            f"line={self.line}, column={self.column})"
        )

    def __str__(self) -> str:
        return f"({self.type.value}, {self.value!r})[line={self.line}, column={self.column}]"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Token):
            return NotImplemented
        return (
            self.type == other.type
            and self.value == other.value
            and self.line == other.line
            and self.column == other.column
        )

    def __hash__(self) -> int:
        return hash((self.type, self.value, self.line, self.column))
