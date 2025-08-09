from typing import Final, Optional
from interpreting.call_stack import (
    CallStack,
    ActivationRecord,
    ActivationRecordType,
)
from syntactic_analysis.ast import *
from utils.visitor import NodeVisitor
from semantic_analysis.symbol_table import (
    FunctionSymbol,
    ProcedureSymbol,
    VariableSymbol,
)
from utils.errors import RuntimeError, ErrorCode


ValueType = Union[int, float, str, bool]


class Interpreter(NodeVisitor[Optional[ValueType]]):
    __slots__ = ("_call_stack", "_functions", "_procedures")

    DEFAULT_VALUES: Final[dict[str, ValueType]] = {
        "int": 0,
        "float": 0.0,
        "string": "",
        "bool": False,
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
        for statement in node.statements:
            result: Optional[Union[ValueType, dict[str, Optional[ValueType]]]] = (
                self.visit(statement)
            )
            if isinstance(result, dict) and "give" in result:
                return result
        return None

    def visit_NodeVariableDeclaration(self, node: NodeVariableDeclaration) -> None:
        current_activation_record: ActivationRecord = self._call_stack.peek()

        for index, identifier in enumerate(node.identifiers):
            variable_value: ValueType = (
                self.visit(node.expressions[index])
                if node.expressions
                else self.DEFAULT_VALUES[node.type.name]
            )
            current_activation_record[identifier.name] = variable_value

    def visit_NodeConstantDeclaration(self, node: NodeConstantDeclaration) -> None:
        current_activation_record: ActivationRecord = self._call_stack.peek()

        for index, identifier in enumerate(node.identifiers):
            constant_value: ValueType = self.visit(node.expressions[index])
            current_activation_record[identifier.name] = constant_value

    def visit_NodeAssignment(self, node: NodeAssignmentStatement) -> None:
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
        function_symbol: Optional[FunctionSymbol] = self._functions.get(
            node.identifier.name
        )
        if function_symbol is None:
            raise RuntimeError(
                ErrorCode.UNDECLARED_IDENTIFIER,
                f"Function '{node.identifier.name}' is not declared.",
            )

        function_arguments: list[ValueType] = [
            self.visit(argument) for argument in (node.arguments or [])
        ]

        function_activation_record: ActivationRecord = ActivationRecord(
            function_symbol.identifier, ActivationRecordType.FUNCTION, 2
        )

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

        raise RuntimeError(
            ErrorCode.FUNCTION_EMPTY_GIVE,
            f"Function '{function_symbol.identifier}' did not give a value.",
        )

    def visit_NodeProcedureCall(self, node: NodeProcedureCall) -> None:
        procedure_symbol: Optional[ProcedureSymbol] = self._procedures.get(
            node.identifier.name
        )
        if procedure_symbol is None:
            raise RuntimeError(
                ErrorCode.UNDECLARED_IDENTIFIER,
                f"Procedure '{node.identifier.name}' is not declared.",
            )

        procedure_arguments: list[ValueType] = [
            self.visit(argument) for argument in (node.arguments or [])
        ]

        procedure_activation_record: ActivationRecord = ActivationRecord(
            procedure_symbol.identifier, ActivationRecordType.PROCEDURE, 2
        )

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

    def visit_NodeIdentifier(self, node: NodeIdentifier) -> ValueType:
        current_activation_record: ActivationRecord = self._call_stack.peek()
        identifier_value: Optional[ValueType] = current_activation_record.get(node.name)

        if identifier_value is None:
            raise RuntimeError(
                ErrorCode.UNDECLARED_IDENTIFIER,
                f"Identifier '{node.name}' is not defined.",
            )
        return identifier_value

    def visit_NodeBinaryOperation(
        self, node: NodeBinaryArithmeticOperation
    ) -> ValueType:
        left_operand: ValueType = self.visit(node.left)
        right_operand: ValueType = self.visit(node.right)
        binary_operator: str = node.operator

        if binary_operator == "+":
            return left_operand + right_operand
        if binary_operator == "-":
            return left_operand - right_operand
        if binary_operator == "*":
            return left_operand * right_operand
        if binary_operator == "/":
            return left_operand / right_operand
        if binary_operator == "//":
            return left_operand // right_operand
        if binary_operator == "%":
            return left_operand % right_operand
        if binary_operator == "**":
            return left_operand**right_operand

        raise RuntimeError(
            ErrorCode.INVALID_OPERATION,
            f"Unknown binary operator '{binary_operator}'",
        )

    def visit_NodeUnaryOperation(self, node: NodeUnaryArithmeticOperation) -> ValueType:
        operand_value: ValueType = self.visit(node.operand)
        unary_operator: str = node.operator

        if unary_operator == "+":
            return +operand_value
        if unary_operator == "-":
            return -operand_value

        raise RuntimeError(
            ErrorCode.INVALID_OPERATION,
            f"Unknown unary operator '{unary_operator}'",
        )

    def visit_NodeIntegerLiteral(self, node: NodeIntegerLiteral) -> int:
        return node.value

    def visit_NodeFloatLiteral(self, node: NodeFloatLiteral) -> float:
        return node.value

    def visit_NodeStringLiteral(self, node: NodeStringLiteral) -> str:
        return node.value

    def visit_NodeBooleanLiteral(self, node: NodeBooleanLiteral) -> bool:
        return node.value
