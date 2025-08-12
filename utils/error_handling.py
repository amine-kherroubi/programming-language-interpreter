from __future__ import annotations
from enum import Enum
from typing import Final
from _1_lexical_analysis.tokens import Token, TokenWithLexeme


class ErrorCode(Enum):
    # Lexical errors
    INVALID_CHARACTER = "INVALID_CHARACTER"
    UNTERMINATED_STRING = "UNTERMINATED_STRING"
    INVALID_NUMBER_FORMAT = "INVALID_NUMBER_FORMAT"

    # Syntactic errors
    UNEXPECTED_TOKEN = "UNEXPECTED_TOKEN"
    WRONG_NUMBER_OF_EXPRESSIONS = "WRONG_NUMBER_OF_EXPRESSIONS"
    UNINITIALIZED_CONSTANT = "UNINITIALIZED_CONSTANT"

    # Semantic errors
    UNDECLARED_IDENTIFIER = "UNDECLARED_IDENTIFIER"
    WRONG_SYMBOL_TYPE = "WRONG_SYMBOL_TYPE"
    WRONG_NUMBER_OF_ARGUMENTS = "WRONG_NUMBER_OF_ARGUMENTS"
    ASSIGNMENT_TO_CONSTANT = "ASSIGNMENT_TO_CONSTANT"
    TYPE_MISMATCH = "TYPE_MISMATCH"
    DUPLICATE_IDENTIFIER = "DUPLICATE_IDENTIFIER"
    INCOMPATIBLE_TYPES = "INCOMPATIBLE_TYPES"
    FUNCTION_EMPTY_GIVE = "FUNCTION_EMPTY_GIVE"
    FUNCTION_NOT_GIVING = "FUNCTION_NOT_GIVING"
    PROCEDURE_GIVING_VALUE = "PROCEDURE_GIVING_VALUE"
    SKIP_STATEMENT_OUTSIDE_WHILE = "SKIP_STATEMENT_OUTSIDE_WHILE"
    STOP_STATEMENT_OUTSIDE_WHILE = "STOP_STATEMENT_OUTSIDE_WHILE"

    # Runtime errors
    INVALID_OPERATION = "INVALID_OPERATION"
    DIVISION_BY_ZERO = "DIVISION_BY_ZERO"
    INVALID_INTIAL_VALUE = "INVALID_INTIAL_VALUE"
    INVALID_TERMINATION_VALUE = "INVALID_TERMINATION_VALUE"
    INVALID_STEP_VALUE = "INVALID_STEP_VALUE"


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


class LexicalError(Error):
    __slots__ = ("position", "line", "column")

    def __init__(
        self, error_code: ErrorCode, message: str, position: int, line: int, column: int
    ) -> None:
        self.position: Final[int] = position
        self.line: Final[int] = line
        self.column: Final[int] = column
        super().__init__(error_code, message)

    def __str__(self) -> str:
        return (
            f"{self.__class__.__name__}: {self.message} "
            f"at position {self.position} (line {self.line}, column {self.column})"
        )

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}(error_code={self.error_code}, "
            f"message='{self.message}', position={self.position}, "
            f"line={self.line}, column={self.column})"
        )


class SyntacticError(Error):
    __slots__ = ("token",)

    def __init__(self, error_code: ErrorCode, message: str, token: Token) -> None:
        self.token: Final[Token] = token
        super().__init__(error_code, message)

    def __str__(self) -> str:
        token_info = f"{self.token.type.value}"
        if isinstance(self.token, TokenWithLexeme):
            token_info += f" '{self.token.lexeme}'"
        return (
            f"{self.__class__.__name__}: {self.message} "
            f"(found: {token_info}) at line {self.token.line}, column {self.token.column}"
        )

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}(error_code={self.error_code}, "
            f"message='{self.message}', token={self.token!r})"
        )


class SemanticError(Error):
    __slots__ = ()

    pass


class RuntimeError(Error):
    __slots__ = ()

    pass
