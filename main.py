from __future__ import annotations
import sys
from _1_lexical_analysis.lexical_analyzer import LexicalAnalyzer, LexicalError
from _1_lexical_analysis.tokens import TokenError
from _2_syntactic_analysis.syntactic_analyser import SyntacticAnalyzer, SyntacticError
from _2_syntactic_analysis.ast import NodeAST
from _3_semantic_analysis.semantic_analyzer import SemanticAnalyzer, SemanticError
from _4_interpretation.interpreter import Interpreter


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
        lexical_analyzer: LexicalAnalyzer = LexicalAnalyzer(program_text)
        syntactic_analyzer: SyntacticAnalyzer = SyntacticAnalyzer(lexical_analyzer)
        abstract_syntax_tree: NodeAST = syntactic_analyzer.parse()
        semantic_analyzer: SemanticAnalyzer = SemanticAnalyzer()
        semantic_analyzer.analyze(abstract_syntax_tree)

        print("Semantic analysis successfully completed.")

        if run_interpreter:
            interpreter: Interpreter = Interpreter()
            interpreter.interpret(abstract_syntax_tree)

    except (
        TokenError,
        LexicalError,
        SyntacticError,
        SemanticError,
        RuntimeError,
    ) as error:
        print(error)

    except Exception as unknown_error:
        print(f"Unhandled Error: {unknown_error}")


if __name__ == "__main__":
    main()
