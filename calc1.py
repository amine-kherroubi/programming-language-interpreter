from typing import Optional, Union, NoReturn


INTEGER, OP, MINUS, WHITESPACE, EOF = "INTEGER", "OP", "MINUS", "WHITESPACE", "EOF"
OPS = ["+", "-", "*", "/"]


class Token(object):
    def __init__(self, type: str, value: Optional[Union[int, str]]) -> None:
        self.type: str = type
        self.value: Optional[Union[int, str]] = value

    def __str__(self) -> str:
        return "Token({type}, {value})".format(type=self.type, value=repr(self.value))

    def __repr__(self) -> str:
        return self.__str__()


class Interpreter(object):
    def __init__(self, text: str) -> None:
        self.text: str = text
        self.pos: int = 0
        self.current_token: Optional[Token] = None

    def error(self) -> NoReturn:
        raise Exception("Error parsing input")

    def get_next_token(self) -> Token:
        current_char: str = self.text[self.pos] if self.pos < len(self.text) else ""
        while current_char == " ":
            self.pos += 1
            if self.pos < len(self.text):
                current_char = self.text[self.pos]
            else:
                break

        if self.pos >= len(self.text):
            return Token(EOF, None)

        if current_char.isdigit():
            integer_str: str = ""
            while current_char.isdigit():
                integer_str += current_char
                self.pos += 1
                if self.pos < len(self.text):
                    current_char = self.text[self.pos]
                else:
                    break
            return Token(INTEGER, int(integer_str))

        if current_char in OPS:
            self.pos += 1
            return Token(OP, current_char)

        self.error()

    def eat(self, token_type: str) -> None:
        if self.current_token and self.current_token.type == token_type:
            self.current_token = self.get_next_token()
        else:
            self.error()

    def expr(self) -> int:
        self.current_token = self.get_next_token()

        left: Token = self.current_token
        self.eat(INTEGER)

        op: Token = self.current_token
        self.eat(OP)

        right: Token = self.current_token
        self.eat(INTEGER)

        result: int = 0
        if isinstance(left.value, int) and isinstance(right.value, int):
            result = eval(f"{left.value} {op.value} {right.value}")
        return result


def main() -> None:
    while True:
        try:
            text: str = input("calc> ")
        except EOFError:
            break
        if not text:
            continue
        interpreter: Interpreter = Interpreter(text)
        result: int = interpreter.expr()
        print(result)


if __name__ == "__main__":
    main()
