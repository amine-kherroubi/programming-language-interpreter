from __future__ import annotations
from typing import Final
from src.commons.error_handling import Error, ErrorCode
from src.lexical_analysis.tokens import (
    Token,
    TokenWithLexeme,
    TokenType,
    LexemeToTokenTypeMappings,
)


class LexicalError(Error):
    __slots__ = ("position", "line", "column")

    def __init__(
        self, error_code: ErrorCode, message: str, position: int, line: int, column: int
    ) -> None:
        if not error_code.name.startswith("LEX_"):
            raise ValueError(f"{error_code} is not a valid lexical error code")
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


class LexicalAnalyzer(object):
    __slots__ = ("source_code", "position", "current_character", "line", "column")

    def __init__(self, source_code: str) -> None:
        self.source_code: str = source_code
        self.position: int = 0
        self.current_character: str | None = source_code[0] if source_code else None
        self.line: int = 1
        self.column: int = 1

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(source_code={self.source_code!r})"

    def __str__(self) -> str:
        return f"Character {self.current_character!r} at position {self.position} (line {self.line}, column {self.column})"

    def _is_at_end(self) -> bool:
        return self.position >= len(self.source_code)

    def _advance(self) -> None:
        if self.current_character == "\n":
            self.line += 1
            self.column = 1
        else:
            self.column += 1

        self.position += 1
        self.current_character = (
            self.source_code[self.position]
            if self.position < len(self.source_code)
            else None
        )

    def _peek(self, offset: int = 1) -> str | None:
        index: int = self.position + offset
        return self.source_code[index] if index < len(self.source_code) else None

    def _skip_whitespace(self) -> None:
        while (
            self.current_character
            and self._is_space(self.current_character)
            and self.current_character != "\n"
        ):
            self._advance()

    def _skip_comment(self) -> None:
        self._advance()
        while self.current_character and self.current_character != "\n":
            self._advance()

    def _skip_consecutive_newlines(self) -> None:
        while self.current_character == "\n":
            self._advance()

    def _is_digit(self, character: str | None) -> bool:
        return "0" <= character <= "9" if character else False

    def _is_alphabetic_underscore_dollar(self, character: str | None) -> bool:
        return (
            (
                ("a" <= character <= "z")
                or ("A" <= character <= "Z")
                or character == "_"
                or character == "$"
            )
            if character
            else False
        )

    def _is_alphanumeric_underscore_dollar(self, character: str | None) -> bool:
        return self._is_digit(character) or self._is_alphabetic_underscore_dollar(
            character
        )

    def _is_space(self, character: str | None) -> bool:
        return character in " \t\n\r\f\v" if character else False

    def _tokenize_number(self) -> TokenWithLexeme:
        start_line: int = self.line
        start_column: int = self.column
        number_lexeme: str = ""
        has_dot: bool = False

        while self.current_character and (
            self._is_digit(self.current_character) or self.current_character == "."
        ):
            if self.current_character == ".":
                if has_dot or not (self._peek() and self._is_digit(self._peek())):
                    break
                has_dot = True
            number_lexeme += self.current_character
            self._advance()

        if not number_lexeme or number_lexeme == ".":
            raise LexicalError(
                ErrorCode.LEX_INVALID_NUMBER_FORMAT,
                f"Invalid number: '{number_lexeme}'",
                self.position,
                self.line,
                self.column,
            )

        return TokenWithLexeme(
            TokenType.NUMBER_LITERAL, start_line, start_column, number_lexeme
        )

    def _tokenize_string(self) -> TokenWithLexeme:
        start_line: int = self.line
        start_column: int = self.column
        assert self.current_character is not None
        quote: str = self.current_character
        self._advance()

        escape_map: Final[dict[str, str]] = {
            "n": "\n",
            "t": "\t",
            "r": "\r",
            "\\": "\\",
            "'": "'",
            '"': '"',
        }

        string_lexeme: str = quote
        while self.current_character and self.current_character != quote:
            if self.current_character == "\n":
                raise LexicalError(
                    ErrorCode.LEX_UNTERMINATED_STRING,
                    "Unterminated string (newline)",
                    self.position,
                    self.line,
                    self.column,
                )

            if self.current_character == "\\":
                self._advance()
                if not self.current_character:
                    raise LexicalError(
                        ErrorCode.LEX_UNTERMINATED_STRING,
                        "Unterminated string (escape end)",
                        self.position,
                        self.line,
                        self.column,
                    )
                string_lexeme += escape_map.get(
                    self.current_character, self.current_character
                )
            else:
                string_lexeme += self.current_character

            self._advance()

        if self.current_character != quote:
            raise LexicalError(
                ErrorCode.LEX_UNTERMINATED_STRING,
                f"Unterminated string, expected '{quote}'",
                self.position,
                self.line,
                self.column,
            )

        string_lexeme += quote

        self._advance()
        return TokenWithLexeme(
            TokenType.STRING_LITERAL, start_line, start_column, string_lexeme
        )

    def _tokenize_identifier(self) -> Token:
        start_line: int = self.line
        start_column: int = self.column
        identifier_lexeme: str = ""

        while self.current_character and (
            self._is_alphanumeric_underscore_dollar(self.current_character)
        ):
            identifier_lexeme += self.current_character
            self._advance()

        if identifier_lexeme in ("true", "false"):
            return TokenWithLexeme(
                TokenType.BOOLEAN_LITERAL, start_line, start_column, identifier_lexeme
            )

        if identifier_lexeme in LexemeToTokenTypeMappings.KEYWORDS:
            return Token(
                LexemeToTokenTypeMappings.KEYWORDS[identifier_lexeme],
                start_line,
                start_column,
            )

        return TokenWithLexeme(
            TokenType.IDENTIFIER, start_line, start_column, identifier_lexeme
        )

    def _tokenize_multi_character_operator(self) -> Token | None:
        start_line: int = self.line
        start_column: int = self.column
        for operator_lexeme, token_type in sorted(
            LexemeToTokenTypeMappings.MULTI_CHARACTER_OPERATORS.items(),
            key=lambda x: len(x[0]),
            reverse=True,
        ):
            if self._matches_operator(operator_lexeme):
                for _ in range(len(operator_lexeme)):
                    self._advance()
                return Token(token_type, start_line, start_column)
        return None

    def _matches_operator(self, operator_lexeme: str) -> bool:
        for i, char in enumerate(operator_lexeme):
            if i == 0:
                if self.current_character != char:
                    return False
            else:
                if self._peek(i) != char:
                    return False
        return True

    def next_token(self) -> Token:
        while True:
            self._skip_whitespace()

            if self.current_character == "#":
                self._skip_comment()
                continue

            if self.current_character is None:
                return Token(TokenType.EOF, self.line, self.column)

            if self.current_character == "\n":
                newline_token: Token = Token(TokenType.NEWLINE, self.line, self.column)
                self._advance()
                self._skip_consecutive_newlines()
                return newline_token

            if self._is_digit(self.current_character) or (
                self.current_character == "."
                and self._peek()
                and self._is_digit(self._peek())
            ):
                return self._tokenize_number()

            if self.current_character in ("'", '"'):
                return self._tokenize_string()

            if (
                self._is_alphabetic_underscore_dollar(self.current_character)
                or self.current_character == "_"
            ):
                return self._tokenize_identifier()

            token: Token | None = self._tokenize_multi_character_operator()
            if token:
                return token

            if (
                self.current_character
                in LexemeToTokenTypeMappings.SINGLE_CHARACTER_LEXEMES
            ):
                token_type: TokenType = (
                    LexemeToTokenTypeMappings.SINGLE_CHARACTER_LEXEMES[
                        self.current_character
                    ]
                )
                start_line: int = self.line
                start_column: int = self.column
                self._advance()
                return Token(token_type, start_line, start_column)

            raise LexicalError(
                ErrorCode.LEX_INVALID_CHARACTER,
                f"Invalid character: '{self.current_character}'",
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
