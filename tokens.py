from typing import Union

INTEGER = "INTEGER"
FLOAT = "FLOAT"
PLUS = "PLUS"
MINUS = "MINUS"
MUL = "MUL"
DIV = "DIV"
LEFT_PARENTHESIS = "LEFT_PARENTHESIS"
RIGHT_PARENTHESIS = "RIGHT_PARENTHESIS"
EOF = "EOF"


class Token:
    __slots__ = (
        "type",
        "value",
    )

    def __init__(self, type: str, value: Union[int, str, float]) -> None:
        self.type: str = type
        self.value: Union[int, str, float] = value

    def __str__(self) -> str:
        return f"({self.type!s}, {self.value!r})"

    def __repr__(self) -> str:
        return f"Token(type={self.type!s}, value={self.value!r})"
