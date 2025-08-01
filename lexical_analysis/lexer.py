from typing import Optional
from lexical_analysis.tokens import Token, TokenType
from utils.exceptions import LexerError


class Lexer:
    __slots__ = ("text", "position", "current_char")

    def __init__(self, text: str) -> None:
        self.text: str = text.strip()
        self.position: int = 0
        self.current_char: Optional[str] = (
            self.text[self.position] if self.text else None
        )

    def advance(self) -> None:
        self.position += 1
        if self.position >= len(self.text):
            self.current_char = None
        else:
            self.current_char = self.text[self.position]

    def peek(self, offset: int = 1) -> Optional[str]:
        peek_pos: int = self.position + offset
        if peek_pos >= len(self.text):
            return None
        return self.text[peek_pos]

    def skip_whitespace(self) -> None:
        while self.current_char and self.current_char.isspace():
            self.advance()

    def tokenize_number(self) -> Token:
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
            self.advance()
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

    def next_token(self) -> Token:
        while self.current_char is not None:
            if self.current_char.isspace():
                self.skip_whitespace()
                continue
            if self.current_char.isdigit() or self.current_char == ".":
                return self.tokenize_number()
            char_to_token: dict[str, TokenType] = {
                "+": TokenType.PLUS,
                "-": TokenType.MINUS,
                "*": TokenType.MUL,
                "/": TokenType.DIV,
                "(": TokenType.LEFT_PARENTHESIS,
                ")": TokenType.RIGHT_PARENTHESIS,
            }
            if self.current_char in char_to_token:
                token_type: TokenType = char_to_token[self.current_char]
                char: str = self.current_char
                self.advance()
                return Token(token_type, char)
            raise LexerError(f"Invalid character: '{self.current_char}'", self.position)
        return Token(TokenType.EOF, "")
