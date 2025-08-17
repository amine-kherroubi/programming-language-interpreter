from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from functools import cached_property
from typing import Final, Union
from utils.error_handling import Error, ErrorCode


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


class LexemeToTokenTypeMappings(object):
    def __new__(cls):
        raise TypeError(f"{cls.__name__} cannot be instantiated")

    SINGLE_CHARACTER_LEXEMS: Final = {
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

    MULTI_CHARACTER_OPERATORS: Final = {
        "->": TokenType.ARROW,
        "**": TokenType.POWER,
        "//": TokenType.FLOOR_DIVIDE,
        "==": TokenType.EQUAL,
        "!=": TokenType.NOT_EQUAL,
        "<=": TokenType.LESS_EQUAL,
        ">=": TokenType.GREATER_EQUAL,
    }

    KEYWORDS: Final = {
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


class TokenError(Error):
    def __init__(self, error_code: ErrorCode, message: str, token: Token) -> None:
        if not error_code.name.startswith("TOK_"):
            raise ValueError(f"{error_code} is not a valid token error code")
        self.token: Final[Token] = token
        super().__init__(error_code, message)

    def __str__(self) -> str:
        return f"{self.__class__.__name__}: {self.message} ({self.token})"

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}(error_code={self.error_code}, "
            f"message='{self.message}', token={self.token})"
        )


@dataclass(frozen=True, slots=True)
class Token(object):
    type: Final[TokenType]
    line: Final[int]
    column: Final[int]

    def __str__(self) -> str:
        return f"Token({self.type.value})[{self.line}:{self.column}]"

    def __post_init__(self) -> None:
        if self.line < 1:
            raise TokenError(
                ErrorCode.TOK_WRONG_POSITIONAL_ATTRIBUTE_VALUE,
                "Line number must be >= 1",
                self,
            )
        if self.column < 1:
            raise TokenError(
                ErrorCode.TOK_WRONG_POSITIONAL_ATTRIBUTE_VALUE,
                "Column number must be >= 1",
                self,
            )


@dataclass(frozen=True, slots=True)
class TokenWithLexeme(Token):
    lexeme: Final[str]

    def __str__(self) -> str:
        return f"Token({self.type.value}: {self.lexeme!r})[{self.line}:{self.column}]"

    def __post_init__(self) -> None:
        Token.__post_init__(self)
        if not self.lexeme:
            raise TokenError(
                ErrorCode.TOK_INVALID_LEXEME, "Lexeme cannot be empty", self
            )

    @cached_property
    def numeric_value(self) -> Union[int, float]:
        if self.type != TokenType.NUMBER_LITERAL:
            raise TokenError(
                ErrorCode.TOK_INVALID_TOKEN_TYPE,
                f"Expected number literal, got {self.type.value}",
                self,
            )

        try:
            return int(self.lexeme) if "." not in self.lexeme else float(self.lexeme)
        except ValueError:
            raise TokenError(
                ErrorCode.TOK_INVALID_LEXEME,
                f"Invalid number format: {self.lexeme}",
                self,
            )

    @cached_property
    def string_value(self) -> str:
        if self.type != TokenType.STRING_LITERAL:
            raise TokenError(
                ErrorCode.TOK_INVALID_TOKEN_TYPE,
                f"Expected string literal, got {self.type.value}",
                self,
            )

        if len(self.lexeme) < 2:
            raise TokenError(
                ErrorCode.TOK_INVALID_LEXEME,
                f"String literal too short: {self.lexeme}",
                self,
            )

        return self.lexeme[1:-1]

    @cached_property
    def boolean_value(self) -> bool:
        if self.type != TokenType.BOOLEAN_LITERAL:
            raise TokenError(
                ErrorCode.TOK_INVALID_TOKEN_TYPE,
                f"Expected boolean literal, got {self.type.value}",
                self,
            )

        if self.lexeme == "true":
            return True
        elif self.lexeme == "false":
            return False
        else:
            raise TokenError(
                ErrorCode.TOK_INVALID_LEXEME,
                f"Invalid boolean value: {self.lexeme}",
                self,
            )

    @cached_property
    def identifier_name(self) -> str:
        if self.type != TokenType.IDENTIFIER:
            raise TokenError(
                ErrorCode.TOK_INVALID_TOKEN_TYPE,
                f"Expected identifier, got {self.type.value}",
                self,
            )

        return self.lexeme
