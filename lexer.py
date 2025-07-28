from typing import Optional, NoReturn
from tokens import Token, INTEGER, PLUS, MINUS, MUL, DIV, EOF


class Lexer:
    __slots__ = ("text", "pos", "current_char")

    def __init__(self, text: str) -> None:
        self.text: str = text
        self.pos: int = 0
        self.current_char: Optional[str] = self.text[self.pos] if self.text else None

    def error(self) -> NoReturn:
        """Raise error for invalid characters"""
        raise Exception("Invalid character")

    def advance(self) -> None:
        """Move to next character in input"""
        self.pos += 1
        if self.pos > len(self.text) - 1:
            self.current_char = None  # End of input
        else:
            self.current_char = self.text[self.pos]

    def skip_whitespace(self) -> None:
        """Skip over spaces"""
        while self.current_char is not None and self.current_char.isspace():
            self.advance()

    def read_number(self) -> int:
        """Read a multi-digit integer from input"""
        digits = ""
        while self.current_char is not None and self.current_char.isdigit():
            digits += self.current_char
            self.advance()
        return int(digits)

    def next_token(self) -> Token:
        """
        Return the next token from input stream.
        Main lexer method - converts characters to tokens.
        """
        while self.current_char is not None:
            # Skip whitespace
            if self.current_char.isspace():
                self.skip_whitespace()
                continue

            # Multi-digit numbers
            if self.current_char.isdigit():
                return Token(INTEGER, self.read_number())

            # Single-character operators
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

            # Unknown character - lexical error
            self.error()

        return Token(EOF, None)
