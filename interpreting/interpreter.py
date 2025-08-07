from typing import Callable, Optional, Union
import operator
from interpreting.call_stack import ActivationRecord, ActivationRecordType, CallStack
from semantic_analysis.symbol_table import ProcedureSymbol
from visitor_pattern.visitor import NodeVisitor
from syntactic_analysis.ast import (
    NodeAST,
    NodeBinaryOperation,
    NodeBlock,
    NodeFunctionCall,
    NodeFunctionDeclaration,
    NodeProcedureCall,
    NodeSubroutineDeclarations,
    NodeProcedureDeclaration,
    NodeVariableDeclarations,
    NodeEmpty,
    NodeAssignmentStatement,
    NodeProgram,
    NodeVariable,
    NodeCompoundStatement,
    NodeNumber,
    NodeUnaryOperation,
    NodeVariableDeclarationGroup,
)
from utils.error_handling import InterpreterError, ErrorCode

ValueType = Union[int, float, str]
NumericType = Union[int, float]


class Interpreter(NodeVisitor[Optional[ValueType]]):
    __slots__ = ("_call_stack",)

    BINARY_OPERATORS: dict[str, Callable[[NumericType, NumericType], NumericType]] = {
        "+": operator.add,
        "-": operator.sub,
        "*": operator.mul,
        "/": operator.truediv,
        "DIV": operator.floordiv,
        "MOD": operator.mod,
    }

    UNARY_OPERATORS: dict[str, Callable[[NumericType], NumericType]] = {
        "+": operator.pos,
        "-": operator.neg,
    }

    TYPES_DEFAULT_VALUES: dict[str, ValueType] = {
        "INTEGER": 0,
        "REAL": 0.0,
    }

    def __init__(self) -> None:
        self._call_stack: CallStack = CallStack()

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}()"

    def __str__(self) -> str:
        return str(self._call_stack)

    def visit_NodeProgram(self, node: NodeProgram) -> None:
        program_record: ActivationRecord = ActivationRecord(
            node.name, ActivationRecordType.PROGRAM, 0
        )
        self._call_stack.push(program_record)
        self.visit(node.block)
        self._call_stack.pop()

    def visit_NodeBlock(self, node: NodeBlock) -> None:
        self.visit(node.variable_declarations)
        self.visit(node.subroutine_declarations)
        self.visit(node.compound_statement)

    def visit_NodeVariableDeclarations(self, node: NodeVariableDeclarations) -> None:
        for declaration in node.variable_declarations:
            self.visit(declaration)

    def visit_NodeVariableDeclarationGroup(
        self, node: NodeVariableDeclarationGroup
    ) -> None:
        default_value: ValueType = self.TYPES_DEFAULT_VALUES[node.type.name]
        for variable in node.members:
            current_record: ActivationRecord = self._call_stack.peek()
            current_record[variable.name] = default_value

    def visit_NodeSubroutineDeclarations(
        self, node: NodeSubroutineDeclarations
    ) -> None:
        for declaration in node.declarations:
            self.visit(declaration)

    def visit_NodeProcedureDeclaration(self, node: NodeProcedureDeclaration) -> None:
        pass

    def visit_NodeFunctionDeclaration(self, node: NodeFunctionDeclaration) -> None:
        pass

    def visit_NodeEmpty(self, node: NodeEmpty) -> None:
        pass

    def visit_NodeAssignmentStatement(self, node: NodeAssignmentStatement) -> None:
        variable_name: str = node.left.name
        result: Optional[ValueType] = self.visit(node.right)
        if result is not None:
            current_record: ActivationRecord = self._call_stack.peek()
            current_record[variable_name] = result

    def visit_NodeVariable(self, node: NodeVariable) -> Optional[ValueType]:
        variable_name: str = node.name
        current_record: ActivationRecord = self._call_stack.peek()
        return current_record.get(variable_name)

    def visit_NodeCompoundStatement(self, node: NodeCompoundStatement) -> None:
        for child in node.children:
            self.visit(child)

    def visit_NodeBinaryOperation(self, node: NodeBinaryOperation) -> NumericType:
        left_val: NumericType = self.visit(node.left)
        right_val: NumericType = self.visit(node.right)
        operator_symbol: str = node.operator.upper()
        if operator_symbol in ("/", "DIV", "MOD") and right_val in (0, 0.0):
            raise InterpreterError(ErrorCode.DIVISION_BY_ZERO, "Cannot divide by zero")
        return self.BINARY_OPERATORS[operator_symbol](left_val, right_val)

    def visit_NodeUnaryOperation(self, node: NodeUnaryOperation) -> NumericType:
        operand_val: NumericType = self.visit(node.operand)
        operator_symbol: str = node.operator.upper()
        return self.UNARY_OPERATORS[operator_symbol](operand_val)

    def visit_NodeNumber(self, node: NodeNumber) -> NumericType:
        return node.value

    def visit_NodeProcedureCall(self, node: NodeProcedureCall) -> None:
        procedure_record: ActivationRecord = ActivationRecord(
            node.name,
            ActivationRecordType.PROCEDURE,
            self._call_stack.peek().nesting_level + 1,
        )
        if not isinstance(node.arguments, NodeEmpty):
            for parameter, argument in zip(node.symbol.parameters, node.arguments):
                procedure_record[parameter.name] = self.visit(argument)
        self._call_stack.push(procedure_record)
        self.visit(node.symbol.block)
        self._call_stack.pop()

    def visit_NodeFunctionCall(self, node: NodeFunctionCall) -> None:
        function_record: ActivationRecord = ActivationRecord(
            node.name,
            ActivationRecordType.FUNCTION,
            self._call_stack.peek().nesting_level + 1,
        )
        if not isinstance(node.arguments, NodeEmpty):
            for parameter, argument in zip(node.symbol.parameters, node.arguments):
                function_record[parameter.name] = self.visit(argument)
        self._call_stack.push(function_record)
        self.visit(node.symbol.block)
        self._call_stack.pop()

    def interpret(self, tree: NodeAST) -> Optional[ValueType]:
        return self.visit(tree)
