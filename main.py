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
        interpreter: Interpreter = Interpreter()
        print(interpreter.interpret(tree=ast))


if __name__ == "__main__":
    main()
