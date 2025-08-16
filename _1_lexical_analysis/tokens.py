from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import Final


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
    FOR = "for"
    TO = "to"
    STEP = "step"
    SKIP = "skip"
    STOP = "stop"
    SHOW = "show"
    NUMBER_TYPE = "number"
    STRING_TYPE = "string"
    BOOLEAN_TYPE = "boolean"
    NUMBER_LITERAL = "NUMBER_LITERAL"
    STRING_LITERAL = "STRING_LITERAL"
    BOOLEAN_LITERAL = "BOOLEAN_LITERAL"
    IDENTIFIER = "IDENTIFIER"
    NEWLINE = "NEWLINE"
    EOF = "EOF"


SINGLE_CHARACTER_LEXEME_TO_TOKEN_TYPE: Final[dict[str, TokenType]] = {
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

MULTI_CHARACTER_OPERATOR_LEXEME_TO_TOKEN_TYPE: Final[dict[str, TokenType]] = {
    "->": TokenType.ARROW,
    "**": TokenType.POWER,
    "//": TokenType.FLOOR_DIVIDE,
    "==": TokenType.EQUAL,
    "!=": TokenType.NOT_EQUAL,
    "<=": TokenType.LESS_EQUAL,
    ">=": TokenType.GREATER_EQUAL,
}

RESERVED_KEYWORD_LEXEME_TO_TOKEN_TYPE: Final[dict[str, TokenType]] = {
    "let": TokenType.LET,
    "keep": TokenType.KEEP,
    "give": TokenType.GIVE,
    "func": TokenType.FUNC,
    "proc": TokenType.PROC,
    "exec": TokenType.EXEC,
    "number": TokenType.NUMBER_TYPE,
    "string": TokenType.STRING_TYPE,
    "boolean": TokenType.BOOLEAN_TYPE,
    "and": TokenType.AND,
    "or": TokenType.OR,
    "not": TokenType.NOT,
    "if": TokenType.IF,
    "elif": TokenType.ELIF,
    "else": TokenType.ELSE,
    "while": TokenType.WHILE,
    "for": TokenType.FOR,
    "to": TokenType.TO,
    "step": TokenType.STEP,
    "skip": TokenType.SKIP,
    "stop": TokenType.STOP,
    "show": TokenType.SHOW,
}


@dataclass(frozen=True, slots=True)
class Token:
    type: Final[TokenType]
    line: Final[int]
    column: Final[int]

    def __str__(self) -> str:
        return f"Token({self.type.value})[{self.line}:{self.column}]"

    def __post_init__(self) -> None:
        if self.line < 1:
            raise ValueError("Line number must be >= 1", self)
        if self.column < 1:
            raise ValueError("Column number must be >= 1", self)


@dataclass(frozen=True, slots=True)
class TokenWithLexeme(Token):
    lexeme: Final[str]

    def __str__(self) -> str:
        return f"Token({self.type.value}: {self.lexeme!r})[{self.line}:{self.column}]"

    def __post_init__(self) -> None:
        Token.__post_init__(self)
        if not self.lexeme:
            raise ValueError("Lexeme cannot be empty", self)
