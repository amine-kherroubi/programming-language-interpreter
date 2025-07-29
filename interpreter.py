"""
Simple arithmetic calculator using recursive descent parsing.

Grammar (BNF):
    expression   ::= term ((PLUS | MINUS) term)*
    term   ::= factor ((MUL | DIV) factor)*
    factor ::= (PLUS | MINUS)? (INTEGER | FLOAT | '(' expression ')')
"""

from lexer import Lexer
from parser import Parser


def main() -> None:
    while True:
        try:
            expression: str = input("interpreter> ")
        except EOFError:
            break
        except KeyboardInterrupt:
            break
        if not expression:
            continue
        lexer = Lexer(expression)
        parser = Parser(lexer)
        result = parser.expression()
        print(result)


if __name__ == "__main__":
    main()
