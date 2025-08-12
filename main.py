import sys
from _1_lexical_analysis.lexical_analyzer import LexicalAnalyzer
from _2_syntactic_analysis.syntactic_analyser import SyntacticAnalyzer
from _2_syntactic_analysis.ast import NodeAST
from _3_semantic_analysis.semantic_analyzer import SemanticAnalyzer
from _4_interpretation.interpreter import Interpreter
from utils.error_handling import (
    LexicalError,
    SyntacticError,
    SemanticError,
    RuntimeError,
)


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python main.py <program_file> [--run]")
        return

    filename: str = sys.argv[1]
    run_interpreter: bool = "--run" in sys.argv

    try:
        with open(filename, "r") as file:
            program_text: str = file.read()
    except FileNotFoundError:
        print(f"Error: file '{filename}' not found.")
        return

    try:
        lexer = LexicalAnalyzer(program_text)
        parser = SyntacticAnalyzer(lexer)
        ast: NodeAST = parser.parse()

        semantic_analyzer = SemanticAnalyzer()
        semantic_analyzer.analyze(ast)

        print("Semantic analysis successfully completed.")

        if run_interpreter:
            interpreter = Interpreter()
            interpreter.interpret(ast)

    except (LexicalError, SyntacticError, SemanticError, RuntimeError) as error:
        print(error)

    except Exception as unknown_error:
        print(f"Unhandled Error: {unknown_error}")


if __name__ == "__main__":
    main()
