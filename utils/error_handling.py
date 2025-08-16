from __future__ import annotations
from enum import Enum
from typing import Final


class ErrorCode(Enum):
    # Token errors
    TOK_INVALID_TOKEN_TYPE = "INVALID_TOKEN_TYPE"
    TOK_INVALID_LEXEME = "INVALID_LEXEME"
    TOK_WRONG_POSITIONAL_ATTRIBUTE_VALUE = "WRONG_POSITIONAL_ATTRIBUTE_VALUE"

    # Lexical errors
    LEX_INVALID_CHARACTER = "INVALID_CHARACTER"
    LEX_UNTERMINATED_STRING = "UNTERMINATED_STRING"
    LEX_INVALID_NUMBER_FORMAT = "INVALID_NUMBER_FORMAT"

    # Syntactic errors
    SYN_UNEXPECTED_TOKEN = "UNEXPECTED_TOKEN"
    SYN_WRONG_NUMBER_OF_EXPRESSIONS = "WRONG_NUMBER_OF_EXPRESSIONS"
    SYN_UNINITIALIZED_CONSTANT = "UNINITIALIZED_CONSTANT"

    # Semantic errors
    SEM_UNDECLARED_IDENTIFIER = "UNDECLARED_IDENTIFIER"
    SEM_WRONG_SYMBOL_TYPE = "WRONG_SYMBOL_TYPE"
    SEM_WRONG_NUMBER_OF_ARGUMENTS = "WRONG_NUMBER_OF_ARGUMENTS"
    SEM_ASSIGNMENT_TO_CONSTANT = "ASSIGNMENT_TO_CONSTANT"
    SEM_TYPE_MISMATCH = "TYPE_MISMATCH"
    SEM_DUPLICATE_IDENTIFIER = "DUPLICATE_IDENTIFIER"
    SEM_INCOMPATIBLE_TYPES = "INCOMPATIBLE_TYPES"
    SEM_FUNCTION_EMPTY_GIVE = "FUNCTION_EMPTY_GIVE"
    SEM_FUNCTION_NOT_GIVING = "FUNCTION_NOT_GIVING"
    SEM_PROCEDURE_GIVING_VALUE = "PROCEDURE_GIVING_VALUE"
    SEM_SKIP_STATEMENT_OUTSIDE_WHILE = "SKIP_STATEMENT_OUTSIDE_WHILE"
    SEM_STOP_STATEMENT_OUTSIDE_WHILE = "STOP_STATEMENT_OUTSIDE_WHILE"

    # Runtime errors
    RUN_INVALID_OPERATION = "INVALID_OPERATION"
    RUN_DIVISION_BY_ZERO = "DIVISION_BY_ZERO"
    RUN_INVALID_INTIAL_VALUE = "INVALID_INTIAL_VALUE"
    RUN_INVALID_TERMINATION_VALUE = "INVALID_TERMINATION_VALUE"
    RUN_INVALID_STEP_VALUE = "INVALID_STEP_VALUE"


class Error(Exception):
    __slots__ = ("error_code", "message")

    def __init__(self, error_code: ErrorCode, message: str) -> None:

        self.error_code: Final[ErrorCode] = error_code
        self.message: Final[str] = message
        super().__init__(str(self))

    def __str__(self) -> str:
        return f"{self.__class__.__name__}: {self.message}"

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(error_code={self.error_code}, message='{self.message}')"
