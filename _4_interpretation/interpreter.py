from __future__ import annotations
from typing import Any, Final, Optional, Union
from _2_syntactic_analysis.ast import *
from _2_syntactic_analysis.ast import NodeForStatement
from _3_semantic_analysis.symbol_table import (
    FunctionSymbol,
    ProcedureSymbol,
    VariableSymbol,
)
from _4_interpretation.call_stack import (
    CallStack,
    ActivationRecord,
    ActivationRecordType,
)
from utils.error_handling import RuntimeError, ErrorCode


ValueType = Union[int, float, str, bool]
NumericType = Union[int, float]


class SkipException(Exception):
    __slots__ = ()


class StopException(Exception):
    __slots__ = ()


class Interpreter(NodeVisitor[Any]):
    __slots__ = ("_call_stack", "_functions", "_procedures")

    DEFAULT_VALUES: Final[dict[str, ValueType]] = {
        "number": 0,
        "string": "",
        "boolean": False,
    }

    def __init__(self) -> None:
        self._call_stack: CallStack = CallStack()
        self._functions: dict[str, FunctionSymbol] = {}
        self._procedures: dict[str, ProcedureSymbol] = {}

    def interpret(self, tree: NodeAST) -> None:
        self.visit(tree)

    def visit_NodeProgram(self, node: NodeProgram) -> None:
        program_activation_record: ActivationRecord = ActivationRecord(
            "program", ActivationRecordType.PROGRAM, 1
        )
        self._call_stack.push(program_activation_record)
        self.visit(node.block)
        self._call_stack.pop()

    def visit_NodeBlock(
        self, node: NodeBlock
    ) -> Optional[dict[str, Optional[ValueType]]]:
        for statement in node.statements or []:
            result: Optional[Union[ValueType, dict[str, Optional[ValueType]]]] = (
                self.visit(statement)
            )
            if isinstance(result, dict) and "give" in result:
                return result
        return None

    def visit_NodeVariableDeclaration(self, node: NodeVariableDeclaration) -> None:
        current_activation_record: ActivationRecord = self._call_stack.peek()

        for index, identifier in enumerate(node.identifiers):
            if node.expressions and index < len(node.expressions):
                variable_value: ValueType = self.visit(node.expressions[index])
            else:
                variable_value: ValueType = self.DEFAULT_VALUES[node.type.name]
            current_activation_record[identifier.name] = variable_value

    def visit_NodeConstantDeclaration(self, node: NodeConstantDeclaration) -> None:
        current_activation_record: ActivationRecord = self._call_stack.peek()

        for index, identifier in enumerate(node.identifiers):
            constant_value: ValueType = self.visit(node.expressions[index])
            current_activation_record[identifier.name] = constant_value

    def visit_NodeAssignmentStatement(self, node: NodeAssignmentStatement) -> None:
        assignment_value: ValueType = self.visit(node.expression)
        current_activation_record: ActivationRecord = self._call_stack.peek()
        current_activation_record[node.identifier.name] = assignment_value

    def visit_NodeGiveStatement(
        self, node: NodeGiveStatement
    ) -> dict[str, Optional[ValueType]]:
        give_value: Optional[ValueType] = (
            self.visit(node.expression) if node.expression else None
        )
        return {"give": give_value}

    def visit_NodeShowStatement(self, node: NodeShowStatement) -> None:
        value: ValueType = self.visit(node.expression)
        print(value)

    def visit_NodeFunctionDeclaration(self, node: NodeFunctionDeclaration) -> None:
        function_parameters: list[VariableSymbol] = [
            VariableSymbol(parameter.identifier.name, parameter.type.name)
            for parameter in (node.parameters or [])
        ]

        function_symbol: FunctionSymbol = FunctionSymbol(
            node.identifier.name,
            function_parameters,
            node.give_type.name,
            node.block,
        )

        self._functions[node.identifier.name] = function_symbol

    def visit_NodeProcedureDeclaration(self, node: NodeProcedureDeclaration) -> None:
        procedure_parameters: list[VariableSymbol] = [
            VariableSymbol(parameter.identifier.name, parameter.type.name)
            for parameter in (node.parameters or [])
        ]

        procedure_symbol: ProcedureSymbol = ProcedureSymbol(
            node.identifier.name,
            procedure_parameters,
            node.block,
        )

        self._procedures[node.identifier.name] = procedure_symbol

    def visit_NodeFunctionCall(self, node: NodeFunctionCall) -> ValueType:
        function_symbol: FunctionSymbol = self._functions.get(node.identifier.name)

        function_arguments: list[ValueType] = [
            self.visit(argument) for argument in (node.arguments or [])
        ]

        current_level = self._call_stack.peek().nesting_level
        function_activation_record: ActivationRecord = ActivationRecord(
            function_symbol.identifier, ActivationRecordType.FUNCTION, current_level + 1
        )

        current_record = self._call_stack.peek()
        for var_name, var_value in current_record.members.items():
            function_activation_record[var_name] = var_value

        if function_symbol.parameters:
            for parameter, argument in zip(
                function_symbol.parameters, function_arguments
            ):
                function_activation_record[parameter.identifier] = argument

        self._call_stack.push(function_activation_record)
        execution_result: Optional[Union[ValueType, dict[str, Optional[ValueType]]]] = (
            self.visit(function_symbol.block)
        )
        self._call_stack.pop()

        if isinstance(execution_result, dict) and "give" in execution_result:
            give_value: Optional[ValueType] = execution_result["give"]
            if give_value is not None:
                return give_value
            else:
                raise RuntimeError(
                    ErrorCode.FUNCTION_EMPTY_GIVE,
                    f"Empty give statement is not allowed in function '{function_symbol.identifier}'.",
                )

        else:
            raise RuntimeError(
                ErrorCode.FUNCTION_NOT_GIVING,
                f"Function '{function_symbol.identifier}' must give a value.",
            )

    def visit_NodeProcedureCall(self, node: NodeProcedureCall) -> None:
        procedure_symbol: ProcedureSymbol = self._procedures.get(node.identifier.name)

        procedure_arguments: list[ValueType] = [
            self.visit(argument) for argument in (node.arguments or [])
        ]

        current_level = self._call_stack.peek().nesting_level
        procedure_activation_record: ActivationRecord = ActivationRecord(
            procedure_symbol.identifier,
            ActivationRecordType.PROCEDURE,
            current_level + 1,
        )

        current_record = self._call_stack.peek()
        for var_name, var_value in current_record.members.items():
            procedure_activation_record[var_name] = var_value

        if procedure_symbol.parameters:
            for parameter, argument in zip(
                procedure_symbol.parameters, procedure_arguments
            ):
                procedure_activation_record[parameter.identifier] = argument

        self._call_stack.push(procedure_activation_record)
        execution_result: Optional[Union[ValueType, dict[str, Optional[ValueType]]]] = (
            self.visit(procedure_symbol.block)
        )
        self._call_stack.pop()

        if (
            isinstance(execution_result, dict)
            and execution_result.get("give") is not None
        ):
            raise RuntimeError(
                ErrorCode.PROCEDURE_GIVING_VALUE,
                f"Procedure '{procedure_symbol.identifier}' cannot give a value.",
            )

    def visit_NodeIfStatement(
        self, node: NodeIfStatement
    ) -> Optional[dict[str, Optional[ValueType]]]:
        if self._evaluate_boolean_expression(node.condition):
            return self.visit(node.block)

        if node.elifs:
            for elif_node in node.elifs:
                if self._evaluate_boolean_expression(elif_node.condition):
                    return self.visit(elif_node.block)

        if node.else_:
            return self.visit(node.else_.block)

        return None

    def visit_NodeWhileStatement(
        self, node: NodeWhileStatement
    ) -> Optional[dict[str, Optional[ValueType]]]:
        while True:
            try:
                termination_condition_is_true: bool = (
                    not self._evaluate_boolean_expression(node.condition)
                )
                if termination_condition_is_true:
                    break

                result = self.visit(node.block)
                if isinstance(result, dict) and "give" in result:
                    return result

            except SkipException:
                continue
            except StopException:
                break

        return None

    def visit_NodeForStatement(self, node: NodeForStatement) -> Any:
        initial_value: ValueType = self.visit(node.initial_assignment.expression)
        if not isinstance(initial_value, NumericType):
            raise RuntimeError(
                ErrorCode.INVALID_INTIAL_VALUE,
                f"Expected number as initial value, got {type(initial_value).__name__}",
            )

        termination_value: ValueType = self.visit(node.termination_expression)
        if not isinstance(termination_value, NumericType):
            raise RuntimeError(
                ErrorCode.INVALID_TERMINATION_VALUE,
                f"Expected number as termination value, got {type(termination_value).__name__}",
            )

        step_value: ValueType
        if node.step_expression:
            step_value = self.visit(node.step_expression)
            if not isinstance(step_value, NumericType):
                raise RuntimeError(
                    ErrorCode.INVALID_STEP_VALUE,
                    f"Expected number as step value, got {type(step_value).__name__}",
                )
        else:
            if initial_value <= termination_value:
                step_value = 1
            else:
                step_value = -1

        self.visit(node.initial_assignment)

        current_activation_record: ActivationRecord = self._call_stack.peek()
        iteration_variable_name: str = node.initial_assignment.identifier.name

        while True:
            try:
                current_value: Optional[ValueType] = current_activation_record.get(
                    iteration_variable_name
                )
                assert isinstance(current_value, NumericType)

                if step_value > 0:
                    if current_value > termination_value:
                        break
                else:
                    if current_value < termination_value:
                        break

                result = self.visit(node.block)
                if isinstance(result, dict) and "give" in result:
                    return result

                current_activation_record[iteration_variable_name] = (
                    current_value + step_value
                )

            except SkipException:
                current_value = current_activation_record.get(iteration_variable_name)
                assert isinstance(current_value, NumericType)
                current_activation_record[iteration_variable_name] = (
                    current_value + step_value
                )
                continue
            except StopException:
                break

        return None

    def visit_NodeSkipStatement(self, node: NodeSkipStatement) -> None:
        raise SkipException()

    def visit_NodeStopStatement(self, node: NodeStopStatement) -> None:
        raise StopException()

    def visit_NodeIdentifier(self, node: NodeIdentifier) -> ValueType:
        current_activation_record: ActivationRecord = self._call_stack.peek()
        identifier_value: Optional[ValueType] = current_activation_record.get(node.name)

        if identifier_value is None:
            raise RuntimeError(
                ErrorCode.UNDECLARED_IDENTIFIER,
                f"Identifier '{node.name}' is not defined.",
            )
        return identifier_value

    def visit_NodeBinaryArithmeticOperation(
        self, node: NodeBinaryArithmeticOperation
    ) -> ValueType:
        left_operand: ValueType = self.visit(node.left)
        right_operand: ValueType = self.visit(node.right)
        binary_operator: str = node.operator

        if binary_operator == "+":
            if isinstance(left_operand, str) or isinstance(right_operand, str):
                return str(left_operand) + str(right_operand)
            return left_operand + right_operand
        if binary_operator == "-":
            return left_operand - right_operand
        if binary_operator == "*":
            return left_operand * right_operand
        if binary_operator == "/":
            if right_operand == 0:
                raise RuntimeError(
                    ErrorCode.DIVISION_BY_ZERO,
                    "Division by zero",
                )
            return left_operand / right_operand
        if binary_operator == "//":
            if right_operand == 0:
                raise RuntimeError(
                    ErrorCode.DIVISION_BY_ZERO,
                    "Division by zero",
                )
            return left_operand // right_operand
        if binary_operator == "%":
            if right_operand == 0:
                raise RuntimeError(
                    ErrorCode.DIVISION_BY_ZERO,
                    "Modulo by zero",
                )
            return left_operand % right_operand
        if binary_operator == "**":
            return left_operand**right_operand

        raise RuntimeError(
            ErrorCode.INVALID_OPERATION,
            f"Unknown binary operator '{binary_operator}'",
        )

    def visit_NodeUnaryArithmeticOperation(
        self, node: NodeUnaryArithmeticOperation
    ) -> ValueType:
        operand_value: ValueType = self.visit(node.operand)
        unary_operator: str = node.operator

        assert isinstance(operand_value, NumericType)
        if unary_operator == "+":
            return +operand_value
        if unary_operator == "-":
            return -operand_value

        raise RuntimeError(
            ErrorCode.INVALID_OPERATION,
            f"Unknown unary operator '{unary_operator}'",
        )

    def visit_NodeBinaryBooleanOperation(
        self, node: NodeBinaryBooleanOperation
    ) -> bool:
        if node.logical_operator == "and":
            left_value = self._evaluate_boolean_expression(node.left)
            if not left_value:
                return False
            right_value = self._evaluate_boolean_expression(node.right)
            return right_value

        elif node.logical_operator == "or":
            left_value = self._evaluate_boolean_expression(node.left)
            if left_value:
                return True
            right_value = self._evaluate_boolean_expression(node.right)
            return right_value

        else:
            raise RuntimeError(
                ErrorCode.INVALID_OPERATION,
                f"Unknown boolean operator '{node.logical_operator}'",
            )

    def visit_NodeUnaryBooleanOperation(self, node: NodeUnaryBooleanOperation) -> bool:
        operand_value = self._evaluate_boolean_expression(node.operand)

        if node.logical_operator == "not":
            return not operand_value
        else:
            raise RuntimeError(
                ErrorCode.INVALID_OPERATION,
                f"Unknown unary boolean operator '{node.logical_operator}'",
            )

    def visit_NodeComparisonExpression(self, node: NodeComparisonExpression) -> bool:
        left_operand: ValueType = self.visit(node.left)
        right_operand: ValueType = self.visit(node.right)
        comparator: str = node.comparator

        if comparator == "==":
            return left_operand == right_operand
        elif comparator == "!=":
            return left_operand != right_operand
        elif comparator == "<":
            return left_operand < right_operand
        elif comparator == ">":
            return left_operand > right_operand
        elif comparator == "<=":
            return left_operand <= right_operand
        elif comparator == ">=":
            return left_operand >= right_operand
        else:
            raise RuntimeError(
                ErrorCode.INVALID_OPERATION,
                f"Unknown comparison operator '{comparator}'",
            )

    def visit_NodeArithmeticExpressionAsBoolean(
        self, node: NodeArithmeticExpressionAsBoolean
    ) -> bool:
        value = self.visit(node.expression)

        if isinstance(value, bool):
            return value
        elif isinstance(value, (int, float)):
            return value != 0
        elif isinstance(value, str):
            return len(value) > 0
        else:
            return bool(value)

    def visit_NodeNumberLiteral(self, node: NodeNumberLiteral) -> Union[int, float]:
        return float(node.lexeme) if "." in node.lexeme else int(node.lexeme)

    def visit_NodeStringLiteral(self, node: NodeStringLiteral) -> str:
        return node.lexeme[1:-1]

    def visit_NodeBooleanLiteral(self, node: NodeBooleanLiteral) -> bool:
        return node.lexeme == "true"

    def _evaluate_boolean_expression(self, node: NodeBooleanExpression) -> bool:
        result = self.visit(node)
        if isinstance(result, bool):
            return result
        else:
            raise RuntimeError(
                ErrorCode.INVALID_OPERATION,
                f"Expected boolean expression, got {type(result).__name__}",
            )
