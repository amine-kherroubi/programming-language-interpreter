from typing import Optional
from lexical_analysis.tokens import Token, TokenType
from utils.error_handling import LexicalError, ErrorCode


class LexicalAnalyzer:
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
        return f"{self.__class__.__name__}(text={self.text!r})"

    def __str__(self) -> str:
        return f"Character {self.current_char!r} at position {self.position} (line {self.line}, column {self.column})"

    @staticmethod
    def _build_reserved_keywords() -> dict[str, TokenType]:
        token_types_list: list[TokenType] = list(TokenType)
        start_index: int = token_types_list.index(TokenType.LET)
        end_index: int = token_types_list.index(TokenType.UNIT_TYPE)
        reserved_keywords: dict[str, TokenType] = {
            token_type.value: token_type
            for token_type in token_types_list[start_index : end_index + 1]
        }
        return reserved_keywords

    @staticmethod
    def _build_single_character_token_types() -> dict[str, TokenType]:
        token_types_list: list[TokenType] = list(TokenType)
        start_index: int = token_types_list.index(TokenType.LEFT_BRACE)
        end_index: int = token_types_list.index(TokenType.MODULO)
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
        while (
            self.current_char is not None
            and self.current_char.isspace()
            and self.current_char != "\n"
        ):
            self._advance()

    def _skip_comment(self) -> None:
        self._advance()
        while self.current_char is not None and self.current_char != "\n":
            self._advance()

    def _skip_other_newlines(self) -> None:
        while self.current_char == "\n":
            self._advance()

    def _tokenize_number(self) -> Token:
        start_line: int = self.line
        start_column: int = self.column
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
        if number_string == "" or number_string == ".":
            raise LexicalError(
                ErrorCode.INVALID_NUMBER_FORMAT,
                "Invalid number format: empty or lone decimal point",
                self.position - 1,
                self.line,
                self.column,
            )
        if has_decimal_point:
            return Token(
                TokenType.REAL_LITERAL, float(number_string), start_line, start_column
            )
        else:
            return Token(
                TokenType.WHOLE_LITERAL, int(number_string), start_line, start_column
            )

    def _tokenize_string(self) -> Token:
        start_line: int = self.line
        start_column: int = self.column
        string_value = ""
        closing_character: str = self.current_char
        self._advance()
        while self.current_char is not None and self.current_char != closing_character:
            if self.current_char == "\n":
                raise LexicalError(
                    ErrorCode.UNTERMINATED_STRING,
                    "Unterminated string literal",
                    self.position,
                    self.line,
                    self.column,
                )
            if self.current_char == "\\":
                self._advance()
                if self.current_char is None:
                    raise LexicalError(
                        ErrorCode.UNTERMINATED_STRING,
                        "Unterminated string literal",
                        self.position,
                        self.line,
                        self.column,
                    )
                if self.current_char == "n":
                    string_value += "\n"
                elif self.current_char == "t":
                    string_value += "\t"
                elif self.current_char == "r":
                    string_value += "\r"
                elif self.current_char == "\\":
                    string_value += "\\"
                elif self.current_char == closing_character:
                    string_value += closing_character
                else:
                    string_value += self.current_char
            else:
                string_value += self.current_char
            self._advance()
        if self.current_char != closing_character:
            raise LexicalError(
                ErrorCode.UNTERMINATED_STRING,
                "Unterminated string literal",
                self.position,
                self.line,
                self.column,
            )
        self._advance()
        return Token(TokenType.TEXT_LITERAL, string_value, start_line, start_column)

    def _tokenize_identifier(self) -> Token:
        start_line: int = self.line
        start_column: int = self.column
        identifier_string: str = ""
        while self.current_char is not None and (
            self.current_char.isalnum() or self.current_char == "_"
        ):
            identifier_string += self.current_char
            self._advance()
        if identifier_string == "true":
            return Token(TokenType.TRUTH_LITERAL, True, start_line, start_column)
        elif identifier_string == "false":
            return Token(TokenType.TRUTH_LITERAL, False, start_line, start_column)
        if identifier_string in self.RESERVED_KEYWORDS:
            return Token(
                self.RESERVED_KEYWORDS[identifier_string],
                identifier_string,
                start_line,
                start_column,
            )
        else:
            return Token(
                TokenType.IDENTIFIER, identifier_string, start_line, start_column
            )

    def _tokenize_two_character_token(self) -> Optional[Token]:
        start_line: int = self.line
        start_column: int = self.column
        if self.current_char == "-" and self._peek() == ">":
            self._advance()
            self._advance()
            return Token(TokenType.ARROW, "->", start_line, start_column)
        elif self.current_char == "*" and self._peek() == "*":
            self._advance()
            self._advance()
            return Token(TokenType.POWER, "**", start_line, start_column)
        elif self.current_char == "/" and self._peek() == "/":
            self._advance()
            self._advance()
            return Token(TokenType.FLOOR_DIVIDE, "//", start_line, start_column)
        return None

    def next_token(self) -> Token:
        self._skip_whitespace()
        while self.current_char == "#":
            self._skip_comment()
            self._skip_whitespace()
        if self.current_char is None:
            return Token(TokenType.EOF, None, self.line, self.column)
        if self.current_char == "\n":
            token = Token(TokenType.NEWLINE, "\n", self.line, self.column)
            self._advance()
            self._skip_other_newlines()
            return token
        if self.current_char.isdigit():
            return self._tokenize_number()
        if (
            self.current_char == "."
            and self._peek() is not None
            and self._peek().isdigit()
        ):
            return self._tokenize_number()
        if self.current_char in ("'", '"'):
            return self._tokenize_string()
        if self.current_char.isalpha() or self.current_char == "_":
            return self._tokenize_identifier()
        two_char_token = self._tokenize_two_character_token()
        if two_char_token is not None:
            return two_char_token
        if self.current_char in self.SINGLE_CHARACTER_TOKEN_TYPES:
            token_type: TokenType = self.SINGLE_CHARACTER_TOKEN_TYPES[self.current_char]
            character: str = self.current_char
            start_line = self.line
            start_column = self.column
            self._advance()
            return Token(token_type, character, start_line, start_column)
        raise LexicalError(
            ErrorCode.INVALID_CHARACTER,
            f"Invalid character: '{self.current_char}'",
            self.position,
            self.line,
            self.column,
        )
