from typing import Optional, Union, NoReturn
from lexer import Lexer
from tokens import Token, INTEGER, PLUS, MINUS, MUL, DIV


class Parser:
    __slots__ = ("lexer", "current_token")

    def __init__(self, lexer: Lexer) -> None:
        self.lexer: Lexer = lexer  # Token source
        self.current_token: Optional[Token] = self.lexer.next_token()  # Lookahead token

    def error(self) -> NoReturn:
        """Raise syntax error for invalid grammar"""
        raise Exception("Invalid syntax")

    def consume(self, token_type: str) -> None:
        """
        Consume a token of expected type and advance to next token.
        Core parsing method - verifies syntax and moves forward.
        """
        if self.current_token and self.current_token.type == token_type:
            self.current_token = self.lexer.next_token()  # Move to next token
        else:
            self.error()  # Expected token not found

    def factor(self) -> int:
        """
        Parse a factor: factor ::= INTEGER
        Handles the highest precedence level (numbers).
        Returns the integer value of the current token.
        """
        token: Optional[Token] = self.current_token  # Save current INTEGER token
        self.consume(INTEGER)  # Verify it's INTEGER and move past it
        if token and isinstance(token.value, int):
            return token.value  # Return the actual number
        self.error()  # Should never reach here

    def term(self) -> Union[int, float]:
        """
        Parse a term: term ::= factor ((MUL | DIV) factor)*
        Handles multiplication and division (higher precedence than +/-).
        Left-associative: 8/4/2 = (8/4)/2 = 1
        """
        result = self.factor()  # Start with first factor

        # Handle zero or more MUL/DIV operations
        while self.current_token and self.current_token.type in (MUL, DIV):
            op = self.current_token
            if op.type == MUL:
                self.consume(MUL)
                result = result * self.factor()  # Multiply by next factor
            elif op.type == DIV:
                self.consume(DIV)
                divisor = self.factor()
                if divisor == 0:
                    raise Exception("Division by zero")
                result = result / divisor  # Divide by next factor (returns float)

        return result

    def expr(self) -> Union[int, float]:
        """
        Parse an expression: expr ::= term ((PLUS | MINUS) term)*
        Handles addition and subtraction (lowest precedence).
        Left-associative: 5-3+1 = (5-3)+1 = 3
        Entry point for parsing - call this to evaluate full expressions.
        """
        result = self.term()  # Start with first term

        # Handle zero or more PLUS/MINUS operations
        while self.current_token and self.current_token.type in (PLUS, MINUS):
            op = self.current_token
            if op.type == PLUS:
                self.consume(PLUS)
                result = result + self.term()  # Add next term
            elif op.type == MINUS:
                self.consume(MINUS)
                result = result - self.term()  # Subtract next term

        return result
