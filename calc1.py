from typing import Optional, Union, NoReturn

INTEGER, PLUS, MINUS, MUL, DIV, EOF = "INTEGER", "PLUS", "MINUS", "MUL", "DIV", "EOF"


class Token:
    __slots__ = ("type", "value")

    def __init__(self, type: str, value: Optional[Union[int, str]]) -> None:
        self.type: str = type
        self.value: Optional[Union[int, str]] = value

    def __str__(self) -> str:
        return f"Token({self.type}, {self.value!r})"

    def __repr__(self) -> str:
        return self.__str__()


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


class Parser:
    __slots__ = ("lexer", "current_token")

    def __init__(self, lexer: Lexer) -> None:
        self.lexer: Lexer = lexer
        self.current_token: Optional[Token] = self.lexer.next_token()

    def error(self) -> NoReturn:
        raise Exception("Invalid syntax")

    def consume(self, token_type: str) -> None:
        if self.current_token and self.current_token.type == token_type:
            self.current_token = self.lexer.next_token()
        else:
            self.error()

    def factor(self) -> int:
        token: Optional[Token] = self.current_token
        self.consume(INTEGER)
        if token and isinstance(token.value, int):
            return token.value
        self.error()

    def term(self) -> Union[int, float]:
        result = self.factor()

        while self.current_token and self.current_token.type in (MUL, DIV):
            op = self.current_token
            if op.type == MUL:
                self.consume(MUL)
                result = result * self.factor()
            elif op.type == DIV:
                self.consume(DIV)
                divisor = self.factor()
                if divisor == 0:
                    raise Exception("Division by zero")
                result = result / divisor

        return result

    def expr(self) -> Union[int, float]:
        result = self.term()

        while self.current_token and self.current_token.type in (PLUS, MINUS):
            op = self.current_token
            if op.type == PLUS:
                self.consume(PLUS)
                result = result + self.term()
            elif op.type == MINUS:
                self.consume(MINUS)
                result = result - self.term()

        return result


def main() -> None:
    while True:
        try:
            expr: str = input("calc> ")
        except EOFError:
            break
        if not expr:
            continue
        lexer = Lexer(expr)
        parser = Parser(lexer)
        result = parser.expr()
        print(result)


if __name__ == "__main__":
    main()
