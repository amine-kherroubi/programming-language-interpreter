from typing import Optional, Union, NoReturn

INTEGER, OP, EOF = "INTEGER", "OP", "EOF"
OPS = ["+", "-", "*", "/"]


class Token:
    def __init__(self, type: str, value: Optional[Union[int, str]]) -> None:
        self.type: str = type
        self.value: Optional[Union[int, str]] = value

    def __str__(self) -> str:
        return f"Token({self.type}, {self.value})"

    def __repr__(self) -> str:
        return self.__str__()


class Interpreter:
    def __init__(self, text: str) -> None:
        self.text: str = text
        self.pos: int = 0
        self.current_token: Optional[Token] = None

    def error(self) -> NoReturn:
        raise Exception("Error parsing input")

    def get_next_token(self) -> Token:
        while self.pos < len(self.text) and self.text[self.pos] == " ":
            self.pos += 1

        if self.pos >= len(self.text):
            return Token(EOF, None)

        current_char: str = self.text[self.pos]

        if current_char.isdigit():
            integer_str: str = ""
            while self.pos < len(self.text) and self.text[self.pos].isdigit():
                integer_str += self.text[self.pos]
                self.pos += 1
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

    def apply_operation(
        self, left: Union[int, float], op: Token, right: Union[int, float]
    ) -> Union[int, float]:
        if op.value == "+":
            return left + right
        elif op.value == "-":
            return left - right
        elif op.value == "*":
            return left * right
        elif op.value == "/":
            if right == 0:
                raise Exception("Division by zero")
            return left / right
        raise Exception("Wrong token value types")

    def expr(self) -> Union[int, float]:
        self.current_token = self.get_next_token()
        left: Token = self.current_token
        self.eat(INTEGER)
        op: Token = self.current_token
        self.eat(OP)
        right: Token = self.current_token
        self.eat(INTEGER)
        result: Union[int, float]
        if (
            isinstance(left.value, int)
            and isinstance(right.value, int)
            and isinstance(op.value, str)
        ):
            result = self.apply_operation(left.value, op, right.value)
        else:
            raise Exception("Invalid token value type")
        while self.pos < len(self.text):
            op: Token = self.current_token
            self.eat(OP)
            right: Token = self.current_token
            self.eat(INTEGER)
            if isinstance(right.value, int) and isinstance(op.value, str):
                result = self.apply_operation(result, op, right.value)
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
        interpreter: Interpreter = Interpreter(text)
        result: Union[int, float] = interpreter.expr()
        print(result)


if __name__ == "__main__":
    main()
