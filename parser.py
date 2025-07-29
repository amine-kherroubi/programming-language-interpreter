from typing import Union, NoReturn
from lexer import Lexer
from tokens import (
    Token,
    INTEGER,
    FLOAT,
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
        self.current_token: Token = self.lexer.next_token()

    def error(self) -> NoReturn:
        raise Exception("Invalid syntax")

    def consume(self, token_type: str) -> None:
        if self.current_token.type == token_type:
            self.current_token = self.lexer.next_token()
        else:
            self.error()

    def factor(self) -> Union[int, float]:
        token: Token = self.current_token
        if token.type == INTEGER:
            self.consume(INTEGER)
            if isinstance(token.value, int):
                return token.value
        elif token.type == FLOAT:
            self.consume(FLOAT)
            if isinstance(token.value, float):
                return token.value
        elif token.type == LEFT_PARENTHESIS:
            self.consume(LEFT_PARENTHESIS)
            result: Union[int, float] = self.expression()
            self.consume(RIGHT_PARENTHESIS)
            return result
        elif token.type == PLUS:
            self.consume(PLUS)
            return self.factor()
        elif token.type == MINUS:
            self.consume(MINUS)
            return -self.factor()
        self.error()

    def term(self) -> Union[int, float]:
        result = self.factor()
        while self.current_token.type in (MUL, DIV):
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

    def expression(self) -> Union[int, float]:
        result = self.term()
        while self.current_token.type in (PLUS, MINUS):
            op = self.current_token
            if op.type == PLUS:
                self.consume(PLUS)
                result = result + self.term()
            elif op.type == MINUS:
                self.consume(MINUS)
                result = result - self.term()
        return result
