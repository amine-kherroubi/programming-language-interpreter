import sys
from typing import Union
from lexical_analysis.lexer import Lexer
from parsing.ast import NodeAST
from parsing.parser import Parser
from interpreting.visitors.interpreter import Interpreter


def format_result(value: Union[int, float]) -> str:
    if isinstance(value, float) and value.is_integer():
        return str(int(value))
    return str(value)


def main() -> None:
    if len(sys.argv) != 2:
        print("Usage: python main.py <program_file>")
        return

    filename: str = sys.argv[1]

    try:
        with open(filename, "r") as file:
            program_text: str = file.read()
    except FileNotFoundError:
        print(f"File '{filename}' not found")
        return

    try:
        lexer: Lexer = Lexer(program_text)
        parser: Parser = Parser(lexer)
        ast: NodeAST = parser.parse()
        interpreter: Interpreter = Interpreter()
        interpreter.interpret(ast)

        for var_name, var_value in interpreter.symbol_table.items():
            print(f"{var_name} = {format_result(var_value)}")

    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
