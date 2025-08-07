from enum import Enum
from lexical_analysis.tokens import Token


class ErrorCode(Enum):
    INVALID_CHARACTER = "Invalid character"
    INVALID_NUMBER_FORMAT = "Invalid number format"
    UNTERMINATED_STRING = "Unterminated string"
    UNEXPECTED_TOKEN = "Unexpected token"
    WRONG_NUMBER_OF_EXPRESSIONS = "Wrong number of expressions"
    UNINITIALIZED_CONSTANT = "Uninitialized constant"
    UNDECLARED_IDENTIFIER = "Undeclared identifier"
    DUPLICATE_DECLARATION = "Duplicate declaration"
    WRONG_NUMBER_OF_ARGUMENTS = "Wrong number of arguments"
    WRONG_SYMBOL_TYPE = "Wrong symbol type"
    DIVISION_BY_ZERO = "Division by zero"


class Error(Exception):
    def __init__(self, error_code: ErrorCode, message: str) -> None:
        self.error_code = error_code
        self.message = message
        super().__init__(str(self))

    def __str__(self) -> str:
        return f"{self.__class__.__name__}: {self.message}"

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(error_code={self.error_code}, message='{self.message}')"


class LexicalError(Error):
    def __init__(
        self, error_code: ErrorCode, message: str, position: int, line: int, column: int
    ) -> None:
        self.position = position
        self.line = line
        self.column = column
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
    def __init__(self, error_code: ErrorCode, message: str, token: Token) -> None:
        self.token = token
        super().__init__(error_code, message)

    def __str__(self) -> str:
        token_info = f"{self.token.type.value}"
        if self.token.value is not None:
            token_info += f" '{self.token.value}'"
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
    pass


class InterpreterError(Error):
    pass
