from enum import Enum
from lexical_analysis.tokens import Token


class ErrorCode(Enum):
    """Enumeration of specific error codes for precise error classification."""

    # Lexical Analysis Errors
    INVALID_CHARACTER = "Invalid character"
    INVALID_NUMBER_FORMAT = "Invalid number format"

    # Syntactic Analysis Errors
    UNEXPECTED_TOKEN = "Unexpected token"

    # Semantic Analysis Errors
    UNDECLARED_IDENTIFIER = "Undeclared identifier"
    DUPLICATE_DECLARATION = "Duplicate declaration"

    # Runtime/Interpreter Errors
    DIVISION_BY_ZERO = "Division by zero"


class Error(Exception):
    """
    Base exception class for all errors.

    Provides structured error information with error code and message.
    Subclasses handle specific positional information requirements.
    """

    __slots__ = ("error_code", "message")

    def __init__(self, error_code: ErrorCode, message: str) -> None:
        """
        Initialize base compiler error.

        Args:
            error_code: Specific error classification
            message: Detailed error description
        """
        self.error_code: ErrorCode = error_code
        self.message: str = message
        super().__init__(self._format_message())

    def _format_message(self) -> str:
        """Format the error message. Override in subclasses for custom formatting."""
        return f"{self.__class__.__name__}: {self.message}"

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(error_code={self.error_code}, message='{self.message}')"


class PositionalError(Error):
    """
    Base class for errors that occur at specific positions in source code.

    Provides line and column tracking for precise error location reporting.
    """

    __slots__ = ("line", "column")

    def __init__(
        self, error_code: ErrorCode, message: str, line: int, column: int
    ) -> None:
        """
        Initialize positional error.

        Args:
            error_code: Specific error classification
            message: Detailed error description
            line: Line number where error occurred
            column: Column number where error occurred
        """
        self.line: int = line
        self.column: int = column
        super().__init__(error_code, message)

    def _format_message(self) -> str:
        """Format message with position information."""
        return f"{self.__class__.__name__}: {self.message} at line {self.line}, column {self.column}"

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}(error_code={self.error_code}, "
            f"message='{self.message}', line={self.line}, column={self.column})"
        )


class LexicalError(PositionalError):
    """
    Exception raised during lexical analysis phase.

    Lexical errors always include position information since they occur
    during character-by-character processing of source text.
    """

    __slots__ = ("position",)

    def __init__(
        self, error_code: ErrorCode, message: str, position: int, line: int, column: int
    ) -> None:
        """
        Initialize lexical error with detailed position information.

        Args:
            error_code: Specific lexical error type
            message: Error description
            position: Character position in source text
            line: Line number
            column: Column number
        """
        self.position: int = position
        super().__init__(error_code, message, line, column)

    def _format_message(self) -> str:
        """Format message with lexical-specific position information."""
        return (
            f"{self.__class__.__name__}: {self.message} "
            f"at position {self.position} (line {self.line}, column {self.column})"
        )


class SyntacticError(PositionalError):
    """
    Exception raised during syntactic analysis phase.

    Syntactic errors always include token information since they occur
    during token-by-token parsing of the input stream.
    """

    __slots__ = ("token",)

    def __init__(self, error_code: ErrorCode, message: str, token: Token) -> None:
        """
        Initialize syntactic error with token information.

        Args:
            error_code: Specific syntactic error type
            message: Error description
            token: Token where error occurred
        """
        self.token: Token = token
        super().__init__(error_code, message, token.line, token.column)

    def _format_message(self) -> str:
        """Format message with token-specific information."""
        token_info = f"{self.token.type.value}"
        if self.token.value is not None:
            token_info += f" '{self.token.value}'"

        return (
            f"{self.__class__.__name__}: {self.message} "
            f"(found: {token_info}) at line {self.line}, column {self.column}"
        )


class SemanticError(Error):
    """
    Exception raised during semantic analysis phase.

    Semantic errors may or may not have precise position information,
    as they deal with program structure and symbol relationships
    rather than specific source locations.
    """

    __slots__ = ()

    def __init__(self, error_code: ErrorCode, message: str) -> None:
        """
        Initialize semantic error.

        Args:
            error_code: Specific semantic error type
            message: Error description
        """
        super().__init__(error_code, message)


class InterpreterError(Error):
    """
    Exception raised during program execution phase.

    Runtime errors typically don't have source position information
    since they occur during execution of the compiled program.
    """

    __slots__ = ()

    def __init__(self, error_code: ErrorCode, message: str) -> None:
        """
        Initialize interpreter/runtime error.

        Args:
            error_code: Specific runtime error type
            message: Error description
        """
        super().__init__(error_code, message)
