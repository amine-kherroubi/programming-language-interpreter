from typing import Optional, Union, Final
from utils.error_handling import LexicalError, ErrorCode
from lexical_analysis.tokens import (
    Token,
    TokenType,
    RESERVED_KEYWORDS,
    SINGLE_CHARACTER_TOKEN_TYPES,
    MULTI_CHAR_OPERATORS,
)


class LexicalAnalyzer:
    __slots__ = ("text", "position", "current_char", "line", "column")

    def __init__(self, text: str) -> None:
        self.text: str = text
        self.position: int = 0
        self.current_char: Optional[str] = text[0] if text else None
        self.line: int = 1
        self.column: int = 1

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(text={self.text!r})"

    def __str__(self) -> str:
        return f"Character {self.current_char!r} at position {self.position} (line {self.line}, column {self.column})"

    def _advance(self) -> None:
        if self.current_char == "\n":
            self.line += 1
            self.column = 1
        else:
            self.column += 1

        self.position += 1
        self.current_char = (
            self.text[self.position] if self.position < len(self.text) else None
        )

    def _peek(self, offset: int = 1) -> Optional[str]:
        index: int = self.position + offset
        return self.text[index] if index < len(self.text) else None

    def _skip_whitespace(self) -> None:
        while (
            self.current_char
            and self.current_char.isspace()
            and self.current_char != "\n"
        ):
            self._advance()

    def _skip_comment(self) -> None:
        self._advance()
        while self.current_char and self.current_char != "\n":
            self._advance()

    def _skip_consecutive_newlines(self) -> None:
        while self.current_char == "\n":
            self._advance()

    def _tokenize_number(self) -> Token:
        start_line: int = self.line
        start_column: int = self.column
        number: str = ""
        has_dot: bool = False

        while self.current_char and (
            self.current_char.isdigit() or self.current_char == "."
        ):
            if self.current_char == ".":
                if has_dot or not (self._peek() and self._peek().isdigit()):
                    break
                has_dot = True
            number += self.current_char
            self._advance()

        if not number or number == ".":
            raise LexicalError(
                ErrorCode.INVALID_NUMBER_FORMAT,
                f"Invalid number: '{number}'",
                self.position,
                self.line,
                self.column,
            )

        value: Union[float, int] = float(number) if has_dot else int(number)
        token_type: TokenType = (
            TokenType.FLOAT_LITERAL if has_dot else TokenType.INT_LITERAL
        )
        return Token(token_type, value, start_line, start_column)

    def _tokenize_string(self) -> Token:
        start_line: int = self.line
        start_column: int = self.column
        quote: str = self.current_char
        self._advance()

        escape_map: Final[dict[str, str]] = {
            "n": "\n",
            "t": "\t",
            "r": "\r",
            "\\": "\\",
            "'": "'",
            '"': '"',
        }

        value: str = ""
        while self.current_char and self.current_char != quote:
            if self.current_char == "\n":
                raise LexicalError(
                    ErrorCode.UNTERMINATED_STRING,
                    "Unterminated string (newline)",
                    self.position,
                    self.line,
                    self.column,
                )

            if self.current_char == "\\":
                self._advance()
                if not self.current_char:
                    raise LexicalError(
                        ErrorCode.UNTERMINATED_STRING,
                        "Unterminated string (escape end)",
                        self.position,
                        self.line,
                        self.column,
                    )
                value += escape_map.get(self.current_char, self.current_char)
            else:
                value += self.current_char

            self._advance()

        if self.current_char != quote:
            raise LexicalError(
                ErrorCode.UNTERMINATED_STRING,
                f"Unterminated string, expected '{quote}'",
                self.position,
                self.line,
                self.column,
            )

        self._advance()
        return Token(TokenType.STRING_LITERAL, value, start_line, start_column)

    def _tokenize_identifier(self) -> Token:
        start_line: int = self.line
        start_column: int = self.column
        identifier: str = ""

        while self.current_char and (
            self.current_char.isalnum() or self.current_char == "_"
        ):
            identifier += self.current_char
            self._advance()

        if identifier == "true":
            return Token(TokenType.BOOL_LITERAL, True, start_line, start_column)
        if identifier == "false":
            return Token(TokenType.BOOL_LITERAL, False, start_line, start_column)
        if identifier in RESERVED_KEYWORDS:
            return Token(
                RESERVED_KEYWORDS[identifier], identifier, start_line, start_column
            )

        return Token(TokenType.IDENTIFIER, identifier, start_line, start_column)

    def _tokenize_multi_character_operator(self) -> Optional[Token]:
        start_line: int = self.line
        start_column: int = self.column
        for operator, token_type in sorted(
            MULTI_CHAR_OPERATORS.items(), key=lambda x: len(x[0]), reverse=True
        ):
            if self._matches_operator(operator):
                for _ in range(len(operator)):
                    self._advance()
                return Token(token_type, operator, start_line, start_column)
        return None

    def _matches_operator(self, operator: str) -> bool:
        for i, char in enumerate(operator):
            if i == 0:
                if self.current_char != char:
                    return False
            else:
                if self._peek(i) != char:
                    return False
        return True

    def next_token(self) -> Token:
        while True:
            self._skip_whitespace()

            if self.current_char == "#":
                self._skip_comment()
                continue

            if self.current_char is None:
                return Token(TokenType.EOF, None, self.line, self.column)

            if self.current_char == "\n":
                token: Token = Token(TokenType.NEWLINE, "\n", self.line, self.column)
                self._advance()
                self._skip_consecutive_newlines()
                return token

            if self.current_char.isdigit() or (
                self.current_char == "." and self._peek() and self._peek().isdigit()
            ):
                return self._tokenize_number()

            if self.current_char in ("'", '"'):
                return self._tokenize_string()

            if self.current_char.isalpha() or self.current_char == "_":
                return self._tokenize_identifier()

            token: Optional[Token] = self._tokenize_multi_character_operator()
            if token:
                return token

            if self.current_char in SINGLE_CHARACTER_TOKEN_TYPES:
                token_type: TokenType = SINGLE_CHARACTER_TOKEN_TYPES[self.current_char]
                char: str = self.current_char
                start_line: int = self.line
                start_column: int = self.column
                self._advance()
                return Token(token_type, char, start_line, start_column)

            raise LexicalError(
                ErrorCode.INVALID_CHARACTER,
                f"Invalid character: '{self.current_char}'",
                self.position,
                self.line,
                self.column,
            )

    def tokenize(self) -> list[Token]:
        tokens: list[Token] = []
        while True:
            token: Token = self.next_token()
            tokens.append(token)
            if token.type == TokenType.EOF:
                break
        return tokens
