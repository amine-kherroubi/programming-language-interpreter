from typing import Optional, Union
from enum import Enum

# Type alias for values that can be stored in tokens
ValueType = Union[int, str, float]


class TokenType(Enum):
    """
    Enumeration of all token types supported by the lexical analyzer.

    Token types are organized into logical groups:
    - Reserved keywords for Pascal-like language constructs
    - Single-character operators and punctuation marks
    - Literal constants and identifiers
    - Special tokens for assignment and end-of-file

    Each token type's value corresponds to its string representation
    in the source code (for keywords and operators) or a descriptive
    name (for constants and identifiers).
    """

    # Reserved keyword token types
    PROGRAM = "PROGRAM"
    VAR = "VAR"
    PROCEDURE = "PROCEDURE"
    FUNCTION = "FUNCTION"
    INTEGER = "INTEGER"
    REAL = "REAL"
    DIV = "DIV"
    MOD = "MOD"
    BEGIN = "BEGIN"
    END = "END"

    # Single-character operator and punctuation token types
    PLUS = "+"
    MINUS = "-"
    MUL = "*"
    TRUE_DIV = "/"
    LEFT_PARENTHESIS = "("
    RIGHT_PARENTHESIS = ")"
    SEMICOLON = ";"
    COLON = ":"
    COMMA = ","
    DOT = "."

    # Literal constant, identifier, and special token types
    INTEGER_CONSTANT = "INTEGER_CONSTANT"
    REAL_CONSTANT = "REAL_CONSTANT"
    ASSIGN = "ASSIGN"
    ID = "ID"
    EOF = "EOF"


class Token(object):
    """
    Represents a single lexical token with its type, value, and source position.

    A token is the basic unit of lexical analysis, containing:
    - The token type (from TokenType enum)
    - The actual value from the source code
    - Line and column position for error reporting and debugging

    This class provides both technical (__repr__) and user-friendly (__str__)
    string representations for different use cases.
    """

    # Use __slots__ for memory efficiency - restricts instance attributes to these only
    __slots__ = ("type", "value", "line", "column")

    def __init__(
        self, token_type: TokenType, value: Optional[ValueType], line: int, column: int
    ) -> None:
        """
        Initialize a token with its type, value, and source position.

        Args:
            token_type: The type of token from the TokenType enum
            value: The actual value from source code (None for some token types)
            line: Line number in source code (1-based)
            column: Column number in source code (1-based)
        """
        self.type: TokenType = token_type  # Token classification
        self.value: Optional[ValueType] = value  # Actual value from source code
        self.line: int = line  # Source line number for error reporting
        self.column: int = column  # Source column number for error reporting

    def __repr__(self) -> str:
        """Return a developer-friendly string representation of the token."""
        return f"{self.__class__.__name__}(type={self.type}, value={self.value!r}, line={self.line}, column={self.column})"

    def __str__(self) -> str:
        """Return a human-readable string representation of the token."""
        return f"({self.type.value}, {self.value!r})[line={self.line}, column={self.column}]"
