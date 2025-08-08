from typing import Callable, Optional, Union
import operator
from interpreting.call_stack import ActivationRecord, ActivationRecordType, CallStack
from visitor_pattern.visitor import NodeVisitor
from syntactic_analysis.ast import (
    NodeAST,
    NodeBinaryOperation,
    NodeBlock,
    NodeAssignment,
    NodeIdentifier,
    NodeNumericLiteral,
    NodeProgram,
    NodeSameTypeVariableDeclarationGroup,
    NodeUnaryOperation,
    NodeUnitUse,
    NodeVariableDeclaration,
)
from utils.error_handling import InterpreterError, ErrorCode

NumericType = Union[int, float]


class Interpreter(NodeVisitor[Optional[NumericType]]):
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

    TYPES_DEFAULT_VALUES: dict[str, NumericType] = {
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
            "Main", ActivationRecordType.PROGRAM, 0
        )
        self._call_stack.push(program_record)
        self.visit(node.block)
        self._call_stack.pop()

    def visit_NodeBlock(self, node: NodeBlock) -> None:
        for statement in node.statements:
            self.visit(statement)

    def visit_NodeVariableDeclaration(self, node: NodeVariableDeclaration) -> None:
        for same_type_group in node.same_type_groups:
            self.visit(same_type_group)

    def visit_NodeSameTypeVariableDeclarationGroup(
        self, node: NodeSameTypeVariableDeclarationGroup
    ) -> None:
        default_value: NumericType = self.TYPES_DEFAULT_VALUES[node.type.name]
        if node.assignable_group is None:
            for identifier in node.identifier_group:
                current_record: ActivationRecord = self._call_stack.peek()
                current_record[identifier.name] = default_value
        else:
            for identifier, expression in zip(
                node.identifier_group, node.assignable_group
            ):
                current_record: ActivationRecord = self._call_stack.peek()
                current_record[identifier.name] = self.visit(expression)

    def visit_NodeAssignmentStatement(self, node: NodeAssignment) -> None:
        id: str = node.identifier.name
        result: Optional[NumericType] = self.visit(node.expression)
        if result is not None:
            current_record: ActivationRecord = self._call_stack.peek()
            current_record[id] = result

    def visit_NodeIdentifier(self, node: NodeIdentifier) -> Optional[NumericType]:
        id: str = node.name
        current_record: ActivationRecord = self._call_stack.peek()
        return current_record.get(id)

    def visit_NodeBinaryOperation(self, node: NodeBinaryOperation) -> NumericType:
        left_val: NumericType = self.visit(node.left_expression)
        right_val: NumericType = self.visit(node.right_expression)
        operator: str = node.operator
        if operator in ("/", "//", "%") and right_val in (0, 0.0):
            raise InterpreterError(ErrorCode.DIVISION_BY_ZERO, "Cannot divide by zero")
        return self.BINARY_OPERATORS[operator](left_val, right_val)

    def visit_NodeUnaryOperation(self, node: NodeUnaryOperation) -> NumericType:
        operand_val: NumericType = self.visit(node.expression)
        operator_symbol: str = node.operator.upper()
        return self.UNARY_OPERATORS[operator_symbol](operand_val)

    def visit_NodeNumericLiteral(self, node: NodeNumericLiteral) -> NumericType:
        return node.value

    def visit_NodeUnitUse(self, node: NodeUnitUse) -> None:
        unit_record: ActivationRecord = ActivationRecord(
            "Anonymous",
            ActivationRecordType.UNIT,
            self._call_stack.peek().nesting_level + 1,
        )
        if node.symbol is not None:
            if node.arguments is not None:
                for parameter, argument in zip(node.symbol.parameters, node.arguments):
                    unit_record[parameter.identifier] = self.visit(argument)
            self._call_stack.push(unit_record)
            self.visit(node.symbol.block)
            self._call_stack.pop()
        else:
            # raise InterpreterError(ErrorCode,"")
            pass

    def interpret(self, tree: NodeAST) -> Optional[NumericType]:
        return self.visit(tree)
