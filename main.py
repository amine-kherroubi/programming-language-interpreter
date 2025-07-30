import sys
from typing import Union
from lexical_analysis.lexer import Lexer
from parsing.parser import Parser
from interpreting.visitors.interpreter import Interpreter
from interpreting.visitors.postfix_translator import PostfixTranslator
from interpreting.visitors.prefix_translator import PrefixTranslator
from utils.exceptions import InterpreterError


def format_result(value: Union[int, float]) -> str:
    if isinstance(value, float) and value.is_integer():
        return str(int(value))
    return str(value)


def main() -> None:
    print("Mathematical Expression Interpreter")
    print("Enter expressions or 'quit' to exit")
    print("Supported operations: +, -, *, /, (), unary +/-")
    print("-" * 50)

    while True:
        try:
            expression = input("interpreter> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break
        if not expression:
            continue
        if expression.lower() in ("quit", "exit", "q"):
            print("Goodbye!")
            break
        if expression.lower() in ("help", "h"):
            print(
                "Enter mathematical expressions like: 2 + 3 * 4, (1 + 2) / 3, -5 + 10"
            )
            continue
        try:
            lexer = Lexer(expression)
            parser = Parser(lexer)
            ast = parser.parse()
            interpreter = Interpreter()
            prefix_translator = PrefixTranslator()
            postfix_translator = PostfixTranslator()
            result = interpreter.interpret(ast)
            prefix = prefix_translator.translate(ast)
            postfix = postfix_translator.translate(ast)
            print(f"Result:  {format_result(result)}")
            print(f"Prefix:  {prefix}")
            print(f"Postfix: {postfix}")
        except InterpreterError as e:
            print(f"Error: {e}")
        except Exception as e:
            print(f"Unexpected error: {e}")
            if "--debug" in sys.argv:
                raise


if __name__ == "__main__":
    main()
