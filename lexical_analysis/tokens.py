from enum import Enum
from typing import Optional, Union, Final


ValueType = Union[int, str, float, bool]


class TokenType(Enum):
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
    FLOOR_DIVIDE = "//"
    POWER = "**"
    LESS = "<"
    GREATER = ">"
    LESS_EQUAL = "<="
    GREATER_EQUAL = ">="
    EQUAL = "=="
    NOT_EQUAL = "!="
    ARROW = "->"
    LET = "let"
    KEEP = "keep"
    GIVE = "give"
    FUNC = "func"
    PROC = "proc"
    EXEC = "exec"
    AND = "and"
    OR = "or"
    NOT = "not"
    IF = "if"
    ELIF = "elif"
    ELSE = "else"
    WHILE = "while"
    SKIP = "skip"
    STOP = "stop"
    SHOW = "show"
    INT_TYPE = "int"
    FLOAT_TYPE = "float"
    STRING_TYPE = "string"
    BOOL_TYPE = "bool"
    INT_LITERAL = "INT_LITERAL"
    FLOAT_LITERAL = "FLOAT_LITERAL"
    STRING_LITERAL = "STRING_LITERAL"
    BOOL_LITERAL = "BOOL_LITERAL"
    IDENTIFIER = "IDENTIFIER"
    NEWLINE = "NEWLINE"
    EOF = "EOF"


RESERVED_KEYWORDS: Final[dict[str, TokenType]] = {
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
    "and": TokenType.AND,
    "or": TokenType.OR,
    "not": TokenType.NOT,
    "if": TokenType.IF,
    "elif": TokenType.ELIF,
    "else": TokenType.ELSE,
    "while": TokenType.WHILE,
    "skip": TokenType.SKIP,
    "stop": TokenType.STOP,
    "show": TokenType.SHOW,
    "true": TokenType.BOOL_LITERAL,
    "false": TokenType.BOOL_LITERAL,
}

SINGLE_CHARACTER_TOKEN_TYPES: Final[dict[str, TokenType]] = {
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
    "<": TokenType.LESS,
    ">": TokenType.GREATER,
}

MULTI_CHAR_OPERATORS: Final[dict[str, TokenType]] = {
    "->": TokenType.ARROW,
    "**": TokenType.POWER,
    "//": TokenType.FLOOR_DIVIDE,
    "==": TokenType.EQUAL,
    "!=": TokenType.NOT_EQUAL,
    "<=": TokenType.LESS_EQUAL,
    ">=": TokenType.GREATER_EQUAL,
}


class Token:
    __slots__ = ("type", "value", "line", "column")

    def __init__(
        self, token_type: TokenType, value: Optional[ValueType], line: int, column: int
    ) -> None:
        self.type: Final[TokenType] = token_type
        self.value: Final[Optional[ValueType]] = value
        self.line: Final[int] = line
        self.column: Final[int] = column

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
