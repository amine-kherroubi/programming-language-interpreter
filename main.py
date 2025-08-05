import sys
from lexical_analysis.lexical_analyzer import LexicalAnalyzer
from syntactic_analysis.ast import NodeAST
from syntactic_analysis.syntactic_analyser import SyntacticAnalyzer
from interpreting.interpreter import Interpreter
from semantic_analysis.semantic_analyzer import SemanticAnalyzer


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
        lexical_analyzer: LexicalAnalyzer = LexicalAnalyzer(program_text)
        syntactic_analyzer: SyntacticAnalyzer = SyntacticAnalyzer(lexical_analyzer)
        ast: NodeAST = syntactic_analyzer.parse()
        semantic_analyzer: SemanticAnalyzer = SemanticAnalyzer()
        semantic_analyzer.analyze(ast)
        interpreter: Interpreter = Interpreter()
        interpreter.interpret(ast)
        print(interpreter)
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
