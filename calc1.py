from typing import Optional, Union, NoReturn

# Token types
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


class Interpreter:
    __slots__ = ("text", "pos", "current_token", "current_char")

    def __init__(self, text: str) -> None:
        self.text: str = text
        self.pos: int = 0
        self.current_token: Optional[Token] = None
        self.current_char: Optional[str] = self.text[self.pos] if self.text else None

    def error(self) -> NoReturn:
        raise Exception("Error parsing input")

    def advance(self) -> None:
        self.pos += 1
        if self.pos > len(self.text) - 1:
            self.current_char = None
        else:
            self.current_char = self.text[self.pos]

    def skip_whitespace(self) -> None:
        while self.current_char is not None and self.current_char.isspace():
            self.advance()

    def integer(self) -> int:
        result = ""
        while self.current_char is not None and self.current_char.isdigit():
            result += self.current_char
            self.advance()
        return int(result)

    def get_next_token(self) -> Token:
        while self.current_char is not None:
            if self.current_char.isspace():
                self.skip_whitespace()
                continue

            if self.current_char.isdigit():
                return Token(INTEGER, self.integer())

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

    def eat(self, token_type: str) -> None:
        if self.current_token and self.current_token.type == token_type:
            self.current_token = self.get_next_token()
        else:
            self.error()

    def factor(self) -> int:
        token: Optional[Token] = self.current_token
        self.eat(INTEGER)
        if token and isinstance(token.value, int):
            return token.value
        self.error()

    def term(self) -> Union[int, float]:
        result = self.factor()

        while self.current_token and self.current_token.type in (MUL, DIV):
            token = self.current_token
            if token.type == MUL:
                self.eat(MUL)
                result = result * self.factor()
            elif token.type == DIV:
                self.eat(DIV)
                divisor = self.factor()
                if divisor == 0:
                    raise Exception("Division by zero")
                result = result / divisor

        return result

    def expr(self) -> Union[int, float]:
        self.current_token = self.get_next_token()

        result = self.term()

        while self.current_token and self.current_token.type in (PLUS, MINUS):
            token = self.current_token
            if token.type == PLUS:
                self.eat(PLUS)
                result = result + self.term()
            elif token.type == MINUS:
                self.eat(MINUS)
                result = result - self.term()

        if self.current_token and self.current_token.type != EOF:
            self.error()

        return result


def main() -> None:
    while True:
        try:
            text: str = input("calc> ")
        except EOFError:
            break
        if not text:
            continue
        interpreter = Interpreter(text)
        result = interpreter.expr()
        print(result)


if __name__ == "__main__":
    main()
