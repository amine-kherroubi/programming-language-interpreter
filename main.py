import sys
from lexical_analysis.lexer import Lexer
from parsing.ast import NodeAST
from parsing.parser import Parser
from interpreting.visitors.interpreter import Interpreter
from interpreting.visitors.symbol_table_builder import SymbolTableBuilder
from interpreting.symbols import SymbolTable_


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
        symbol_table: SymbolTable_ = SymbolTable_()
        symbol_table_builder: SymbolTableBuilder = SymbolTableBuilder(symbol_table)
        symbol_table_builder.build(ast)
        interpreter: Interpreter = Interpreter()
        interpreter.interpret(ast)
        # print(interpreter)
        print(symbol_table)
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
