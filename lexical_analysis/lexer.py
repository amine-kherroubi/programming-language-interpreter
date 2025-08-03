from typing import Optional, Dict
from lexical_analysis.tokens import Token, TokenType
from utils.exceptions import LexerError


class Lexer:
    __slots__ = ("text", "position", "current_char")

    RESERVED_KEYWORD_TOKEN_TYPES: Dict[str, TokenType] = {
        "PROGRAM": TokenType.PROGRAM,
        "VAR": TokenType.VAR,
        "PROCEDURE": TokenType.PROCEDURE,
        "FUNCTION": TokenType.FUNCTION,
        "INTEGER": TokenType.INTEGER,
        "REAL": TokenType.REAL,
        "BEGIN": TokenType.BEGIN,
        "END": TokenType.END,
        "DIV": TokenType.INTEGER_DIV,
        "MOD": TokenType.MOD,
    }

    SINGLE_CHAR_TOKEN_TYPES: Dict[str, TokenType] = {
        "+": TokenType.PLUS,
        "-": TokenType.MINUS,
        "*": TokenType.MUL,
        "/": TokenType.TRUE_DIV,
        "(": TokenType.LEFT_PARENTHESIS,
        ")": TokenType.RIGHT_PARENTHESIS,
        ";": TokenType.SEMICOLON,
        "=": TokenType.ASSIGN,
        ".": TokenType.DOT,
        ":": TokenType.COLON,
        ",": TokenType.COMMA,
    }

    def __init__(self, text: str) -> None:
        self.text: str = text
        self.position: int = 0
        self.current_char: Optional[str] = (
            self.text[self.position] if self.text else None
        )

    def _advance(self) -> None:
        self.position: int = self.position + 1
        if self.position >= len(self.text):
            self.current_char: Optional[str] = None
        else:
            self.current_char: Optional[str] = self.text[self.position]

    def _peek(self, offset: int = 1) -> Optional[str]:
        peek_position: int = self.position + offset
        if peek_position >= len(self.text):
            return None
        return self.text[peek_position]

    def _skip_whitespace(self) -> None:
        while self.current_char is not None and self.current_char.isspace():
            self._advance()

    def _skip_comment(self) -> None:
        while self.current_char is not None and self.current_char != "}":
            self._advance()
        if self.current_char == "}":
            self._advance()

    def _tokenize_number(self) -> Token:
        number_string: str = ""
        has_decimal_point: bool = False
        while self.current_char is not None and (
            self.current_char.isdigit() or self.current_char == "."
        ):
            if self.current_char == ".":
                if has_decimal_point:
                    raise LexerError(
                        "Invalid number format: multiple decimal points", self.position
                    )
                has_decimal_point = True
            number_string += self.current_char
            self._advance()
        if number_string == ".":
            raise LexerError(
                "Invalid number format: lone decimal point", self.position - 1
            )
        if has_decimal_point:
            return Token(TokenType.REAL_CONSTANT, float(number_string))
        else:
            return Token(TokenType.INTEGER_CONSTANT, int(number_string))

    def _tokenize_identifier(self) -> Token:
        identifier_string: str = ""
        while self.current_char is not None and (
            self.current_char.isalnum() or self.current_char == "_"
        ):
            identifier_string += self.current_char
            self._advance()
        uppercase_identifier: str = identifier_string.upper()
        if uppercase_identifier in self.RESERVED_KEYWORD_TOKEN_TYPES:
            return Token(
                self.RESERVED_KEYWORD_TOKEN_TYPES[uppercase_identifier],
                identifier_string,
            )
        else:
            return Token(TokenType.ID, identifier_string)

    def next_token(self) -> Token:
        self._skip_whitespace()
        if self.current_char == "{":
            self._skip_comment()
            return self.next_token()
        if not self.current_char:
            return Token(TokenType.EOF, None)
        if self.current_char.isdigit():
            return self._tokenize_number()
        if self.current_char == ".":
            next_character: Optional[str] = self._peek()
            if next_character is not None and next_character.isdigit():
                return self._tokenize_number()
        if self.current_char.isalpha() or self.current_char == "_":
            return self._tokenize_identifier()
        if self.current_char in self.SINGLE_CHAR_TOKEN_TYPES:
            token_type: TokenType = self.SINGLE_CHAR_TOKEN_TYPES[self.current_char]
            character: str = self.current_char
            self._advance()
            return Token(token_type, character)
        raise LexerError(f"Invalid character: '{self.current_char}'", self.position)
