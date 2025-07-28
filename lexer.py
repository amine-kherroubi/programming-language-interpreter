from typing import Optional, NoReturn
from tokens import (
    Token,
    INTEGER,
    PLUS,
    MINUS,
    MUL,
    DIV,
    LEFT_PARENTHESIS,
    RIGHT_PARENTHESIS,
    EOF,
)


class Lexer:
    __slots__ = ("text", "pos", "current_char")

    def __init__(self, text: str) -> None:
        self.text: str = text
        self.pos: int = 0
        self.current_char: Optional[str] = self.text[self.pos] if self.text else None

    def error(self) -> NoReturn:
        raise Exception("Invalid character")

    def advance(self) -> None:
        self.pos += 1
        if self.pos > len(self.text) - 1:
            self.current_char = None
        else:
            self.current_char = self.text[self.pos]

    def skip_whitespace(self) -> None:
        while self.current_char is not None and self.current_char.isspace():
            self.advance()

    def read_number(self) -> int:
        digits = ""
        while self.current_char is not None and self.current_char.isdigit():
            digits += self.current_char
            self.advance()
        return int(digits)

    def next_token(self) -> Token:
        while self.current_char is not None:
            if self.current_char.isspace():
                self.skip_whitespace()
                continue

            if self.current_char == "(":
                self.advance()
                return Token(LEFT_PARENTHESIS, "(")

            if self.current_char == ")":
                self.advance()
                return Token(RIGHT_PARENTHESIS, ")")

            if self.current_char.isdigit():
                return Token(INTEGER, self.read_number())

            if self.current_char == "+":
                self.advance()
                return Token(PLUS, "+")

            if self.current_char == "-":
                self.advance()
                return Token(MINUS, "-")

            if self.current_char == "*":
                self.advance()
                return Token(MUL, "*")

            if self.current_char == "/":
                self.advance()
                return Token(DIV, "/")

            self.error()

        return Token(EOF, None)
