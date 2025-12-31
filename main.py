from __future__ import annotations
import sys
from src.lexical_analysis.lexical_analyzer import LexicalAnalyzer, LexicalError
from src.lexical_analysis.tokens import TokenError
from src.syntactic_analysis.syntactic_analyser import (
    SyntacticAnalyzer,
    SyntacticError,
)
from src.syntactic_analysis.ast import NodeAST
from src.semantic_analysis.semantic_analyzer import SemanticAnalyzer, SemanticError
from src.interpretation.interpreter import Interpreter


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python main.py <program_file>")
        return

    filename: str = sys.argv[1]

    try:
        with open(filename, "r") as file:
            program_text: str = file.read()
    except FileNotFoundError:
        return

    try:
        lexical_analyzer: LexicalAnalyzer = LexicalAnalyzer(program_text)
        syntactic_analyzer: SyntacticAnalyzer = SyntacticAnalyzer(lexical_analyzer)
        abstract_syntax_tree: NodeAST = syntactic_analyzer.parse()
        semantic_analyzer: SemanticAnalyzer = SemanticAnalyzer()
        semantic_analyzer.analyze(abstract_syntax_tree)

        interpreter: Interpreter = Interpreter()
        interpreter.interpret(abstract_syntax_tree)

    except (TokenError, LexicalError, SyntacticError, SemanticError, RuntimeError):
        return
    except Exception:
        return


if __name__ == "__main__":
    main()
