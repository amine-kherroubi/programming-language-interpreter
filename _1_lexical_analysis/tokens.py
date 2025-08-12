from __future__ import annotations
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
    "skip": TokenType.SKIP,
    "stop": TokenType.STOP,
    "show": TokenType.SHOW,
}


class Token(object):
    __slots__ = ("type", "line", "column")

    def __init__(self, token_type: TokenType, line: int, column: int) -> None:
        self.type: Final[TokenType] = token_type
        self.line: Final[int] = line
        self.column: Final[int] = column

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(type={self.type}, line={self.line}, column={self.column})"

    def __str__(self) -> str:
        return f"({self.type.value})[line={self.line}, column={self.column}]"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Token):
            return False
        return (
            self.type == other.type
            and self.line == other.line
            and self.column == other.column
        )

    def __hash__(self) -> int:
        return hash((self.type, self.line, self.column))


class TokenWithLexeme(Token):
    __slots__ = ("lexeme",)

    def __init__(
        self, token_type: TokenType, lexeme: str, line: int, column: int
    ) -> None:
        super().__init__(token_type, line, column)
        self.lexeme: Final[str] = lexeme

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}(type={self.type}, lexeme={self.lexeme!r}, "
            f"line={self.line}, column={self.column})"
        )

    def __str__(self) -> str:
        return f"({self.type.value}: {self.lexeme!r})[line={self.line}, column={self.column}]"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, TokenWithLexeme):
            return False
        return (
            self.type == other.type
            and self.lexeme == other.lexeme
            and self.line == other.line
            and self.column == other.column
        )

    def __hash__(self) -> int:
        return hash((self.type, self.lexeme, self.line, self.column))
