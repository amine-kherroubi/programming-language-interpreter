from typing import Optional
from interpreting.call_stack import (
    CallStack,
    ActivationRecord,
    ActivationRecordType,
    NumericType,
)
from syntactic_analysis.ast import *
from visitor_pattern.visitor import NodeVisitor
from semantic_analysis.symbol_table import (
    FunctionSymbol,
    ProcedureSymbol,
    VariableSymbol,
)
from utils.error_handling import InterpreterError, ErrorCode


class Interpreter(NodeVisitor[Optional[NumericType]]):
    __slots__ = ("_call_stack", "_functions", "_procedures")

    def __init__(self) -> None:
        self._call_stack = CallStack()
        self._functions: dict[str, FunctionSymbol] = {}
        self._procedures: dict[str, ProcedureSymbol] = {}

    def interpret(self, tree: NodeAST) -> None:
        self.visit(tree)

    def visit_NodeProgram(self, node: NodeProgram) -> None:
        ar = ActivationRecord("main", ActivationRecordType.PROGRAM, 1)
        self._call_stack.push(ar)
        self.visit(node.block)
        self._call_stack.pop()

    def visit_NodeBlock(self, node: NodeBlock) -> None:
        for stmt in node.statements:
            result = self.visit(stmt)
            if isinstance(result, dict) and "return" in result:
                return result

    def visit_NodeVariableDeclaration(self, node: NodeVariableDeclaration) -> None:
        for i, identifier in enumerate(node.identifiers):
            value = self.visit(node.expressions[i]) if node.expressions else None
            self._call_stack.peek()[identifier.name] = value

    def visit_NodeConstantDeclaration(self, node: NodeConstantDeclaration) -> None:
        for i, identifier in enumerate(node.identifiers):
            value = self.visit(node.expressions[i])
            self._call_stack.peek()[identifier.name] = value

    def visit_NodeAssignment(self, node: NodeAssignment) -> None:
        value = self.visit(node.expression)
        self._call_stack.peek()[node.identifier.name] = value

    def visit_NodeGiveStatement(
        self, node: NodeGiveStatement
    ) -> dict[str, Optional[NumericType]]:
        value = self.visit(node.expression) if node.expression else None
        return {"return": value}

    def visit_NodeFunctionDeclaration(self, node: NodeFunctionDeclaration) -> None:
        self._functions[node.name.name] = FunctionSymbol(
            node.name.name,
            [
                VariableSymbol(p.identifier.name, p.type.name)
                for p in node.parameters or []
            ],
            node.return_type.name,
            node.block,
        )

    def visit_NodeProcedureDeclaration(self, node: NodeProcedureDeclaration) -> None:
        self._procedures[node.name.name] = ProcedureSymbol(
            node.name.name,
            [
                VariableSymbol(p.identifier.name, p.type.name)
                for p in node.parameters or []
            ],
            node.block,
        )

    def visit_NodeFunctionCall(self, node: NodeFunctionCall) -> NumericType:
        symbol = self._functions.get(node.name.name)
        if symbol is None:
            raise InterpreterError(
                ErrorCode.UNDECLARED_IDENTIFIER,
                f"Function '{node.name.name}' is not declared.",
            )

        args = [self.visit(arg) for arg in node.arguments or []]
        ar = ActivationRecord(symbol.identifier, ActivationRecordType.FUNCTION, 2)

        if symbol.parameters:
            for param, arg in zip(symbol.parameters, args):
                ar[param.identifier] = arg

        self._call_stack.push(ar)
        result = self.visit(symbol.block)
        self._call_stack.pop()

        if isinstance(result, dict) and "return" in result:
            return result["return"]

        raise InterpreterError(
            ErrorCode.EXPRESSION_UNIT_EMPTY_RETURN,
            f"Function '{symbol.identifier}' did not return a value.",
        )

    def visit_NodeProcedureCall(self, node: NodeProcedureCall) -> None:
        symbol = self._procedures.get(node.name.name)
        if symbol is None:
            raise InterpreterError(
                ErrorCode.UNDECLARED_IDENTIFIER,
                f"Procedure '{node.name.name}' is not declared.",
            )

        args = [self.visit(arg) for arg in node.arguments or []]
        ar = ActivationRecord(symbol.identifier, ActivationRecordType.PROCEDURE, 2)

        if symbol.parameters:
            for param, arg in zip(symbol.parameters, args):
                ar[param.identifier] = arg

        self._call_stack.push(ar)
        result = self.visit(symbol.block)
        self._call_stack.pop()

        if isinstance(result, dict) and result.get("return") is not None:
            raise InterpreterError(
                ErrorCode.PROCEDURE_UNIT_RETURNING_VALUE,
                f"Procedure '{symbol.identifier}' cannot return a value.",
            )

    def visit_NodeIdentifier(self, node: NodeIdentifier) -> NumericType:
        value = self._call_stack.peek().get(node.name)
        if value is None:
            raise InterpreterError(
                ErrorCode.UNDECLARED_IDENTIFIER,
                f"Identifier '{node.name}' is not defined.",
            )
        return value

    def visit_NodeBinaryOperation(self, node: NodeBinaryOperation) -> NumericType:
        left = self.visit(node.left)
        right = self.visit(node.right)
        op = node.operator

        if op == "+":
            return left + right
        if op == "-":
            return left - right
        if op == "*":
            return left * right
        if op == "/":
            return left / right
        if op == "//":
            return left // right
        if op == "%":
            return left % right
        if op == "**":
            return left**right

        raise InterpreterError(
            ErrorCode.INVALID_OPERATION,
            f"Unknown binary operator '{op}'",
        )

    def visit_NodeUnaryOperation(self, node: NodeUnaryOperation) -> NumericType:
        operand = self.visit(node.operand)

        if node.operator == "+":
            return +operand
        if node.operator == "-":
            return -operand

        raise InterpreterError(
            ErrorCode.INVALID_OPERATION,
            f"Unknown unary operator '{node.operator}'",
        )

    def visit_NodeIntegerLiteral(self, node: NodeIntegerLiteral) -> int:
        return node.value

    def visit_NodeFloatLiteral(self, node: NodeFloatLiteral) -> float:
        return node.value

    def visit_NodeStringLiteral(self, node: NodeStringLiteral) -> str:
        return node.value

    def visit_NodeBooleanLiteral(self, node: NodeBooleanLiteral) -> bool:
        return node.value
