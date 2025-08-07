from typing import Optional
from lexical_analysis.tokens import Token, TokenType
from utils.error_handling import LexicalError, ErrorCode


class LexicalAnalyzer(object):
    __slots__ = ("text", "position", "current_char", "line", "column")

    def __init__(self, text: str) -> None:
        self.text: str = text
        self.position: int = 0
        self.current_char: Optional[str] = (
            self.text[self.position] if self.text else None
        )
        self.line: int = 1
        self.column: int = 1

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(text={self.text})"

    def __str__(self) -> str:
        return f"Character {self.current_char!r} at position {self.position} (line {self.line}, column {self.column})"

    @staticmethod
    def _build_reserved_keywords() -> dict[str, TokenType]:
        token_types_list: list[TokenType] = list(TokenType)
        start_index: int = token_types_list.index(TokenType.PROGRAM)
        end_index: int = token_types_list.index(TokenType.END)
        reserved_keywords: dict[str, TokenType] = {
            token_type.value: token_type
            for token_type in token_types_list[start_index : end_index + 1]
        }
        return reserved_keywords

    @staticmethod
    def _build_single_character_token_types() -> dict[str, TokenType]:
        token_types_list: list[TokenType] = list(TokenType)
        start_index: int = token_types_list.index(TokenType.PLUS)
        end_index: int = token_types_list.index(TokenType.DOT)
        single_character_token_types: dict[str, TokenType] = {
            token_type.value: token_type
            for token_type in token_types_list[start_index : end_index + 1]
        }
        return single_character_token_types

    RESERVED_KEYWORDS: dict[str, TokenType] = _build_reserved_keywords()
    SINGLE_CHARACTER_TOKEN_TYPES: dict[str, TokenType] = (
        _build_single_character_token_types()
    )

    def _advance(self) -> None:
        if self.current_char == "\n":
            self.line += 1
            self.column = 1
        else:
            self.column += 1
        self.position += 1
        if self.position >= len(self.text):
            self.current_char = None
        else:
            self.current_char = self.text[self.position]

    def _peek(self, offset: int = 1) -> Optional[str]:
        peek_position: int = self.position + offset
        if peek_position >= len(self.text):
            return None
        return self.text[peek_position]

    def _skip_whitespace(self) -> None:
        while self.current_char is not None and self.current_char.isspace():
            self._advance()

    def _skip_comment(self) -> None:
        while self.current_char is not None and self.current_char != "}":
            self._advance()
        if self.current_char == "}":
            self._advance()

    def _tokenize_number(self) -> Token:
        number_string: str = ""
        has_decimal_point: bool = False
        while self.current_char is not None and (
            self.current_char.isdigit() or self.current_char == "."
        ):
            if self.current_char == ".":
                if has_decimal_point:
                    raise LexicalError(
                        ErrorCode.INVALID_NUMBER_FORMAT,
                        "Invalid number format: multiple decimal points",
                        self.position,
                        self.line,
                        self.column,
                    )
                has_decimal_point = True
            number_string += self.current_char
            self._advance()
        if number_string == ".":
            raise LexicalError(
                ErrorCode.INVALID_NUMBER_FORMAT,
                "Invalid number format: lone decimal point",
                self.position - 1,
                self.line,
                self.column,
            )
        if has_decimal_point:
            return Token(
                TokenType.REAL_CONSTANT, float(number_string), self.line, self.column
            )
        else:
            return Token(
                TokenType.INTEGER_CONSTANT, int(number_string), self.line, self.column
            )

    def _tokenize_identifier(self) -> Token:
        identifier_string: str = ""
        while self.current_char is not None and (
            self.current_char.isalnum() or self.current_char == "_"
        ):
            identifier_string += self.current_char
            self._advance()
        uppercase_identifier: str = identifier_string.upper()
        if uppercase_identifier in self.RESERVED_KEYWORDS:
            return Token(
                self.RESERVED_KEYWORDS[uppercase_identifier],
                identifier_string,
                self.line,
                self.column,
            )
        else:
            return Token(TokenType.ID, identifier_string, self.line, self.column)

    def next_token(self) -> Token:
        self._skip_whitespace()
        while self.current_char == "{":
            self._skip_comment()
            self._skip_whitespace()
        if self.current_char is None:
            return Token(TokenType.EOF, None, self.line, self.column)
        if self.current_char.isdigit():
            return self._tokenize_number()
        if self.current_char == ".":
            next_character: Optional[str] = self._peek()
            if next_character is not None and next_character.isdigit():
                return self._tokenize_number()
        if self.current_char.isalpha() or self.current_char == "_":
            return self._tokenize_identifier()
        if self.current_char == ":" and self._peek(1) == "=":
            self._advance()
            self._advance()
            return Token(TokenType.ASSIGN, ":=", self.line, self.column)
        if self.current_char in self.SINGLE_CHARACTER_TOKEN_TYPES:
            token_type: TokenType = self.SINGLE_CHARACTER_TOKEN_TYPES[self.current_char]
            character: str = self.current_char
            self._advance()
            return Token(token_type, character, self.line, self.column)
        raise LexicalError(
            ErrorCode.INVALID_CHARACTER,
            f"Invalid character: '{self.current_char}'",
            self.position,
            self.line,
            self.column,
        )
