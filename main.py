import sys
from lexical_analysis.lexical_analyzer import LexicalAnalyzer
from syntactic_analysis.ast import NodeAST
from syntactic_analysis.parser import SyntacticAnalyzer
from interpreting.interpreter import Interpreter
from semantic_analysis.semantic_analyzer import SemanticAnalyzer
from semantic_analysis.symbol_table import SymbolTable_


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
        symbol_table: SymbolTable_ = SymbolTable_()
        semantic_analyzer: SemanticAnalyzer = SemanticAnalyzer(symbol_table)
        semantic_analyzer.build(ast)
        interpreter: Interpreter = Interpreter()
        interpreter.interpret(ast)
        print(symbol_table)
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
