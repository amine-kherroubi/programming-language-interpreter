from typing import Optional, Union

INTEGER = "INTEGER"
PLUS = "PLUS"
MINUS = "MINUS"
MUL = "MUL"
DIV = "DIV"
LEFT_PARENTHESIS = "LEFT_PARENTHESIS"
RIGHT_PARENTHESIS = "RIGHT_PARENTHESIS"
EOF = "EOF"


class Token:
    __slots__ = ("type", "value")

    def __init__(self, type: str, value: Optional[Union[int, str]]) -> None:
        self.type: str = type
        self.value: Optional[Union[int, str]] = value

    def __str__(self) -> str:
        return f"Token({self.type}, {self.value!r})"

    def __repr__(self) -> str:
        return self.__str__()
