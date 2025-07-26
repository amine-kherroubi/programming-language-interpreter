from typing import Optional, Union, NoReturn

INTEGER, OP, EOF = "INTEGER", "OP", "EOF"
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
        # Skip whitespace
        while self.pos < len(self.text) and self.text[self.pos] == " ":
            self.pos += 1

        # Check if we've reached the end
        if self.pos >= len(self.text):
            return Token(EOF, None)

        current_char: str = self.text[self.pos]

        # Handle multi-digit integers
        if current_char.isdigit():
            integer_str: str = ""
            while self.pos < len(self.text) and self.text[self.pos].isdigit():
                integer_str += self.text[self.pos]
                self.pos += 1
            return Token(INTEGER, int(integer_str))

        # Handle operators
        if current_char in OPS:
            self.pos += 1
            return Token(OP, current_char)

        self.error()

    def eat(self, token_type: str) -> None:
        if self.current_token and self.current_token.type == token_type:
            self.current_token = self.get_next_token()
        else:
            self.error()

    def expr(self) -> Union[int, float]:
        self.current_token = self.get_next_token()

        # Get left operand
        left: Token = self.current_token
        self.eat(INTEGER)

        # Get operator
        op: Token = self.current_token
        self.eat(OP)

        # Get right operand
        right: Token = self.current_token
        self.eat(INTEGER)

        # Perform calculation
        if (
            isinstance(left.value, int)
            and isinstance(right.value, int)
            and isinstance(op.value, str)
        ):
            if op.value == "+":
                return left.value + right.value
            elif op.value == "-":
                return left.value - right.value
            elif op.value == "*":
                return left.value * right.value
            elif op.value == "/":
                if right.value == 0:
                    raise Exception("Division by zero")
                return left.value / right.value

        return 0


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
