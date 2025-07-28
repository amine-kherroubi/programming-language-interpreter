from typing import Optional, Union, NoReturn
from lexer import Lexer
from tokens import (
    Token,
    INTEGER,
    PLUS,
    MINUS,
    MUL,
    DIV,
    LEFT_PARENTHESIS,
    RIGHT_PARENTHESIS,
)


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

    def factor(self) -> Union[int, float]:
        token: Optional[Token] = self.current_token
        if token and token.type == INTEGER:
            self.consume(INTEGER)
            if isinstance(token.value, int):
                return token.value
        elif token and token.type == LEFT_PARENTHESIS:
            self.consume(LEFT_PARENTHESIS)
            result: Union[int, float] = self.expr()
            self.consume(RIGHT_PARENTHESIS)
            return result
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
