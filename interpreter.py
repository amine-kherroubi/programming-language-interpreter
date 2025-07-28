"""
Simple arithmetic calculator using recursive descent parsing.

Grammar (BNF):
    expr   ::= term ((PLUS | MINUS) term)*
    term   ::= factor ((MUL | DIV) factor)*
    factor ::= INTEGER
"""

from lexer import Lexer
from parser import Parser


def main() -> None:
    """
    Main REPL (Read-Eval-Print Loop) for the calculator.
    Continuously reads expressions, parses and evaluates them, then prints results.
    """
    while True:
        try:
            expr: str = input("calc> ")
        except EOFError:
            break
        except KeyboardInterrupt:
            break
        if not expr:  # Skip empty lines
            continue

        lexer = Lexer(expr)
        parser = Parser(lexer)
        result = parser.expr()
        print(result)


if __name__ == "__main__":
    main()
