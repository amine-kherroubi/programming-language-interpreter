from typing import Optional
from lexical_analysis.tokens import Token, TokenType
from utils.exceptions import LexerError


class Lexer:
    __slots__ = ("text", "position", "current_char")

    RESERVED_KEYWORD_TYPES: dict[str, TokenType] = {
        "start": TokenType.START,
        "end": TokenType.END,
    }

    SINGLE_CHAR_TOKEN_TYPES: dict[str, TokenType] = {
        "+": TokenType.PLUS,
        "-": TokenType.MINUS,
        "*": TokenType.MUL,
        "/": TokenType.DIV,
        "(": TokenType.LEFT_PARENTHESIS,
        ")": TokenType.RIGHT_PARENTHESIS,
        ";": TokenType.SEMICOLON,
        "=": TokenType.ASSIGN,
        ".": TokenType.DOT,
    }

    def __init__(self, text: str) -> None:
        self.text: str = text
        self.position: int = 0
        self.current_char: Optional[str] = (
            self.text[self.position] if self.text else None
        )

    def _advance(self) -> None:
        self.position += 1
        if self.position >= len(self.text):
            self.current_char = None
        else:
            self.current_char = self.text[self.position]

    def _peek(self, offset: int = 1) -> Optional[str]:
        peek_pos: int = self.position + offset
        if peek_pos >= len(self.text):
            return None
        return self.text[peek_pos]

    def _skip_whitespace(self) -> None:
        while self.current_char and self.current_char.isspace():
            self._advance()

    def _tokenize_number(self) -> Token:
        number_str: str = ""
        has_dot: bool = False
        while self.current_char and (
            self.current_char.isdigit() or self.current_char == "."
        ):
            if self.current_char == ".":
                if has_dot:
                    raise LexerError(
                        "Invalid number format: multiple decimal points", self.position
                    )
                has_dot = True
            number_str += self.current_char
            self._advance()
        if number_str == ".":
            raise LexerError(
                "Invalid number format: lone decimal point", self.position - 1
            )
        try:
            if has_dot:
                return Token(TokenType.FLOAT, float(number_str))
            else:
                return Token(TokenType.INTEGER, int(number_str))
        except ValueError:
            raise LexerError(
                f"Invalid number format: {number_str}", self.position - len(number_str)
            )

    def _tokenize_id(self) -> Token:
        id_str: str = ""
        while self.current_char and (
            self.current_char.isalnum() or self.current_char == "_"
        ):
            id_str += self.current_char
            self._advance()
        return (
            Token(self.RESERVED_KEYWORD_TYPES[id_str], id_str)
            if id_str in self.RESERVED_KEYWORD_TYPES
            else Token(TokenType.ID, id_str)
        )

    def next_token(self) -> Token:
        self._skip_whitespace()
        if not self.current_char:
            return Token(TokenType.EOF, None)
        if self.current_char.isdigit():
            return self._tokenize_number()
        if self.current_char == "." and (next_char := self._peek(1)):
            if next_char.isdigit():
                return self._tokenize_number()
        if self.current_char.isalpha() or self.current_char == "_":
            return self._tokenize_id()
        if self.current_char in self.SINGLE_CHAR_TOKEN_TYPES:
            token_type: TokenType = self.SINGLE_CHAR_TOKEN_TYPES[self.current_char]
            char: str = self.current_char
            self._advance()
            return Token(token_type, char)
        raise LexerError(f"Invalid character: '{self.current_char}'", self.position)
