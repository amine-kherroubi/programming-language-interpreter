"""
Simple arithmetic calculator using recursive descent parsing.

Grammar (BNF):
    expression   ::= term ((PLUS | MINUS) term)*
    term   ::= factor ((MUL | DIV) factor)*
    factor ::= (PLUS | MINUS)? (INTEGER | FLOAT | '(' expression ')')
"""

from lexer import Lexer
from parser import NodeAST, Parser
from interpreter import Interpreter


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
        lexer: Lexer = Lexer(expression)
        parser: Parser = Parser(lexer)
        ast: NodeAST = parser.parse()
        interpreter = Interpreter()
        print(interpreter.evaluate(node=ast))


if __name__ == "__main__":
    main()
