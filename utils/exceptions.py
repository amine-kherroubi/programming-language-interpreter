from lexical_analysis.tokens import Token


class InterpreterError(Exception):
    __slots__ = ()

    def __init__(self, message: str) -> None:
        super().__init__(message)


class LexerError(Exception):
    __slots__ = ()

    def __init__(self, message: str, position: int) -> None:
        super().__init__(f"{message} at position {position}")


class ParserError(Exception):
    __slots__ = ()

    def __init__(self, message: str, token: Token) -> None:
        super().__init__(f"{message}: unexpected token {token}")


class SymbolTableError(Exception):
    __slots__ = ()

    def __init__(self, message: str) -> None:
        super().__init__(message)
