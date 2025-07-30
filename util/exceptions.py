from lexical_analysis.tokens import Token


class InterpreterError(Exception):
    pass


class LexerError(InterpreterError):
    def __init__(self, message: str, position: int) -> None:
        super().__init__(f"{message} at position {position}")
        self.position = position


class ParserError(InterpreterError):
    def __init__(self, message: str, token: Token) -> None:
        super().__init__(f"{message}: unexpected token {token}")
        self.token: Token = token
