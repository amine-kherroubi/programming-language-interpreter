from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Generic, NoReturn, TypeVar
from _1_lexical_analysis.tokens import Token

T = TypeVar("T")


class NodeVisitor(Generic[T], ABC):
    def visit(self, node: NodeAST) -> T:
        return node.accept(self)

    def _raise_not_implemented(self, node: NodeAST) -> NoReturn:
        raise NotImplementedError(
            f"Visitor {self.__class__.__name__} does not implement visit_{node.__class__.__name__}"
        )

    @abstractmethod
    def visit_NodeProgram(self, node: NodeProgram) -> T: ...

    def visit_NodeBlock(self, node: NodeBlock) -> T:
        return self._raise_not_implemented(node)

    def visit_NodeType(self, node: NodeType) -> T:
        return self._raise_not_implemented(node)

    def visit_NodeIdentifier(self, node: NodeIdentifier) -> T:
        return self._raise_not_implemented(node)

    def visit_NodeVariableDeclaration(self, node: NodeVariableDeclaration) -> T:
        return self._raise_not_implemented(node)

    def visit_NodeConstantDeclaration(self, node: NodeConstantDeclaration) -> T:
        return self._raise_not_implemented(node)

    def visit_NodeAssignmentStatement(self, node: NodeAssignmentStatement) -> T:
        return self._raise_not_implemented(node)

    def visit_NodeGiveStatement(self, node: NodeGiveStatement) -> T:
        return self._raise_not_implemented(node)

    def visit_NodeShowStatement(self, node: NodeShowStatement) -> T:
        return self._raise_not_implemented(node)

    def visit_NodeElif(self, node: NodeElif) -> T:
        return self._raise_not_implemented(node)

    def visit_NodeElse(self, node: NodeElse) -> T:
        return self._raise_not_implemented(node)

    def visit_NodeIfStatement(self, node: NodeIfStatement) -> T:
        return self._raise_not_implemented(node)

    def visit_NodeWhileStatement(self, node: NodeWhileStatement) -> T:
        return self._raise_not_implemented(node)

    def visit_NodeForStatement(self, node: NodeForStatement) -> T:
        return self._raise_not_implemented(node)

    def visit_NodeSkipStatement(self, node: NodeSkipStatement) -> T:
        return self._raise_not_implemented(node)

    def visit_NodeStopStatement(self, node: NodeStopStatement) -> T:
        return self._raise_not_implemented(node)

    def visit_NodeParameter(self, node: NodeParameter) -> T:
        return self._raise_not_implemented(node)

    def visit_NodeFunctionDeclaration(self, node: NodeFunctionDeclaration) -> T:
        return self._raise_not_implemented(node)

    def visit_NodeProcedureDeclaration(self, node: NodeProcedureDeclaration) -> T:
        return self._raise_not_implemented(node)

    def visit_NodeFunctionCall(self, node: NodeFunctionCall) -> T:
        return self._raise_not_implemented(node)

    def visit_NodeProcedureCall(self, node: NodeProcedureCall) -> T:
        return self._raise_not_implemented(node)

    def visit_NodeBinaryArithmeticOperation(
        self, node: NodeBinaryArithmeticOperation
    ) -> T:
        return self._raise_not_implemented(node)

    def visit_NodeUnaryArithmeticOperation(
        self, node: NodeUnaryArithmeticOperation
    ) -> T:
        return self._raise_not_implemented(node)

    def visit_NodeArithmeticExpressionAsBoolean(
        self, node: NodeArithmeticExpressionAsBoolean
    ) -> T:
        return self._raise_not_implemented(node)

    def visit_NodeBinaryBooleanOperation(self, node: NodeBinaryBooleanOperation) -> T:
        return self._raise_not_implemented(node)

    def visit_NodeUnaryBooleanOperation(self, node: NodeUnaryBooleanOperation) -> T:
        return self._raise_not_implemented(node)

    def visit_NodeComparisonExpression(self, node: NodeComparisonExpression) -> T:
        return self._raise_not_implemented(node)

    def visit_NodeNumberLiteral(self, node: NodeNumberLiteral) -> T:
        return self._raise_not_implemented(node)

    def visit_NodeStringLiteral(self, node: NodeStringLiteral) -> T:
        return self._raise_not_implemented(node)

    def visit_NodeBooleanLiteral(self, node: NodeBooleanLiteral) -> T:
        return self._raise_not_implemented(node)


class NodeAST(ABC):
    __slots__ = ()

    @abstractmethod
    def accept(self, visitor: NodeVisitor[T]) -> T: ...

    @abstractmethod
    def __repr__(self) -> str: ...


class NodeStatement(NodeAST):
    __slots__ = ()


class NodeExpression(NodeAST):
    __slots__ = ()


class NodeArithmeticExpression(NodeExpression):
    __slots__ = ()


class NodeBooleanExpression(NodeExpression):
    __slots__ = ()


class NodeBlock(NodeAST):
    __slots__ = ("statements",)

    def __init__(self, statements: list[NodeStatement] | None) -> None:
        self.statements: list[NodeStatement] | None = statements

    def accept(self, visitor: NodeVisitor[T]) -> T:
        return visitor.visit_NodeBlock(self)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(statements={self.statements})"


class NodeProgram(NodeAST):
    __slots__ = ("block",)

    def __init__(self, block: NodeBlock) -> None:
        self.block: NodeBlock = block

    def accept(self, visitor: NodeVisitor[T]) -> T:
        return visitor.visit_NodeProgram(self)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(block={self.block})"


class NodeType(NodeAST):
    __slots__ = ("name",)

    def __init__(self, token: Token) -> None:
        self.name: str = token.type.value

    def accept(self, visitor: NodeVisitor[T]) -> T:
        return visitor.visit_NodeType(self)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name={self.name})"


class NodeIdentifier(NodeArithmeticExpression):
    __slots__ = ("name",)

    def __init__(self, name: str) -> None:
        self.name: str = name

    def accept(self, visitor: NodeVisitor[T]) -> T:
        return visitor.visit_NodeIdentifier(self)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name={self.name})"


class NodeVariableDeclaration(NodeStatement):
    __slots__ = ("type", "identifiers", "expressions")

    def __init__(
        self,
        var_type: NodeType,
        identifiers: list[NodeIdentifier],
        expressions: list[NodeExpression] | None = None,
    ) -> None:
        self.type: NodeType = var_type
        self.identifiers: list[NodeIdentifier] = identifiers
        self.expressions: list[NodeExpression] | None = expressions

    def accept(self, visitor: NodeVisitor[T]) -> T:
        return visitor.visit_NodeVariableDeclaration(self)

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}(type={self.type}, "
            f"identifiers={self.identifiers}, expressions={self.expressions})"
        )


class NodeConstantDeclaration(NodeStatement):
    __slots__ = ("type", "identifiers", "expressions")

    def __init__(
        self,
        const_type: NodeType,
        identifiers: list[NodeIdentifier],
        expressions: list[NodeExpression],
    ) -> None:
        self.type: NodeType = const_type
        self.identifiers: list[NodeIdentifier] = identifiers
        self.expressions: list[NodeExpression] = expressions

    def accept(self, visitor: NodeVisitor[T]) -> T:
        return visitor.visit_NodeConstantDeclaration(self)

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}(type={self.type}, "
            f"identifiers={self.identifiers}, expressions={self.expressions})"
        )


class NodeAssignmentStatement(NodeStatement):
    __slots__ = ("identifier", "expression")

    def __init__(self, identifier: NodeIdentifier, expression: NodeExpression) -> None:
        self.identifier: NodeIdentifier = identifier
        self.expression: NodeExpression = expression

    def accept(self, visitor: NodeVisitor[T]) -> T:
        return visitor.visit_NodeAssignmentStatement(self)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(identifier={self.identifier}, expression={self.expression})"


class NodeGiveStatement(NodeStatement):
    __slots__ = ("expression",)

    def __init__(self, expression: NodeExpression | None) -> None:
        self.expression: NodeExpression | None = expression

    def accept(self, visitor: NodeVisitor[T]) -> T:
        return visitor.visit_NodeGiveStatement(self)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(expression={self.expression})"


class NodeShowStatement(NodeStatement):
    __slots__ = ("expression",)

    def __init__(self, expression: NodeExpression) -> None:
        self.expression: NodeExpression = expression

    def accept(self, visitor: NodeVisitor[T]) -> T:
        return visitor.visit_NodeShowStatement(self)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(expression={self.expression})"


class NodeElif(NodeAST):
    __slots__ = ("condition", "block")

    def __init__(
        self,
        condition: NodeBooleanExpression,
        block: NodeBlock,
    ) -> None:
        self.condition: NodeBooleanExpression = condition
        self.block: NodeBlock = block

    def accept(self, visitor: NodeVisitor[T]) -> T:
        return visitor.visit_NodeElif(self)

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}(condition={self.condition}, block={self.block})"
        )


class NodeElse(NodeAST):
    __slots__ = ("block",)

    def __init__(
        self,
        block: NodeBlock,
    ) -> None:
        self.block: NodeBlock = block

    def accept(self, visitor: NodeVisitor[T]) -> T:
        return visitor.visit_NodeElse(self)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(block={self.block})"


class NodeIfStatement(NodeStatement):
    __slots__ = ("condition", "block", "elifs", "else_")

    def __init__(
        self,
        condition: NodeBooleanExpression,
        block: NodeBlock,
        elifs: list[NodeElif] | None,
        else_: NodeElse | None,
    ) -> None:
        self.condition: NodeBooleanExpression = condition
        self.block: NodeBlock = block
        self.elifs: list[NodeElif] | None = elifs
        self.else_: NodeElse | None = else_

    def accept(self, visitor: NodeVisitor[T]) -> T:
        return visitor.visit_NodeIfStatement(self)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(condition={self.condition}, block={self.block}, elifs={self.elifs}, else_={self.else_})"


class NodeWhileStatement(NodeStatement):
    __slots__ = ("condition", "block")

    def __init__(
        self,
        condition: NodeBooleanExpression,
        block: NodeBlock,
    ) -> None:
        self.condition: NodeBooleanExpression = condition
        self.block: NodeBlock = block

    def accept(self, visitor: NodeVisitor[T]) -> T:
        return visitor.visit_NodeWhileStatement(self)

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}(condition={self.condition}, block={self.block})"
        )


class NodeForStatement(NodeStatement):
    __slots__ = (
        "initial_assignment",
        "termination_expression",
        "step_expression",
        "block",
    )

    def __init__(
        self,
        initial_assignment: NodeAssignmentStatement,
        termination_expression: NodeArithmeticExpression,
        step_expression: NodeArithmeticExpression | None,
        block: NodeBlock,
    ) -> None:
        self.initial_assignment: NodeAssignmentStatement = initial_assignment
        self.termination_expression: NodeArithmeticExpression = termination_expression
        self.step_expression: NodeArithmeticExpression | None = step_expression
        self.block: NodeBlock = block

    def accept(self, visitor: NodeVisitor[T]) -> T:
        return visitor.visit_NodeForStatement(self)

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}(initial_assignment={self.initial_assignment}, "
            f"termination_expression={self.termination_expression}, "
            f"step_expression={self.step_expression}, block={self.block})"
        )


class NodeSkipStatement(NodeStatement):
    __slots__ = ()

    def accept(self, visitor: NodeVisitor[T]) -> T:
        return visitor.visit_NodeSkipStatement(self)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}()"


class NodeStopStatement(NodeStatement):
    __slots__ = ()

    def accept(self, visitor: NodeVisitor[T]) -> T:
        return visitor.visit_NodeStopStatement(self)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}()"


class NodeParameter(NodeAST):
    __slots__ = ("identifier", "type")

    def __init__(self, identifier: NodeIdentifier, type: NodeType) -> None:
        self.identifier: NodeIdentifier = identifier
        self.type: NodeType = type

    def accept(self, visitor: NodeVisitor[T]) -> T:
        return visitor.visit_NodeParameter(self)

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}(identifier={self.identifier}, type={self.type})"
        )


class NodeFunctionDeclaration(NodeStatement):
    __slots__ = ("identifier", "parameters", "give_type", "block")

    def __init__(
        self,
        identifier: NodeIdentifier,
        parameters: list[NodeParameter] | None,
        give_type: NodeType,
        block: NodeBlock,
    ) -> None:
        self.identifier: NodeIdentifier = identifier
        self.parameters: list[NodeParameter] | None = parameters
        self.give_type: NodeType = give_type
        self.block: NodeBlock = block

    def accept(self, visitor: NodeVisitor[T]) -> T:
        return visitor.visit_NodeFunctionDeclaration(self)

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}(identifier={self.identifier}, parameters={self.parameters}, "
            f"give_type={self.give_type}, block={self.block})"
        )


class NodeProcedureDeclaration(NodeStatement):
    __slots__ = ("identifier", "parameters", "block")

    def __init__(
        self,
        identifier: NodeIdentifier,
        parameters: list[NodeParameter] | None,
        block: NodeBlock,
    ) -> None:
        self.identifier: NodeIdentifier = identifier
        self.parameters: list[NodeParameter] | None = parameters
        self.block: NodeBlock = block

    def accept(self, visitor: NodeVisitor[T]) -> T:
        return visitor.visit_NodeProcedureDeclaration(self)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(identifier={self.identifier}, parameters={self.parameters}, block={self.block})"


class NodeFunctionCall(NodeArithmeticExpression):
    __slots__ = ("identifier", "arguments")

    def __init__(
        self,
        identifier: NodeIdentifier,
        arguments: list[NodeExpression] | None,
    ) -> None:
        self.identifier: NodeIdentifier = identifier
        self.arguments: list[NodeExpression] | None = arguments

    def accept(self, visitor: NodeVisitor[T]) -> T:
        return visitor.visit_NodeFunctionCall(self)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(identifier={self.identifier}, arguments={self.arguments})"


class NodeProcedureCall(NodeStatement):
    __slots__ = ("identifier", "arguments")

    def __init__(
        self,
        identifier: NodeIdentifier,
        arguments: list[NodeExpression] | None,
    ) -> None:
        self.identifier: NodeIdentifier = identifier
        self.arguments: list[NodeExpression] | None = arguments

    def accept(self, visitor: NodeVisitor[T]) -> T:
        return visitor.visit_NodeProcedureCall(self)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(identifier={self.identifier}, arguments={self.arguments})"


class NodeBinaryArithmeticOperation(NodeArithmeticExpression):
    __slots__ = ("left", "operator", "right")

    def __init__(
        self,
        left: NodeArithmeticExpression,
        operator: str,
        right: NodeArithmeticExpression,
    ) -> None:
        self.left: NodeArithmeticExpression = left
        self.operator: str = operator
        self.right: NodeArithmeticExpression = right

    def accept(self, visitor: NodeVisitor[T]) -> T:
        return visitor.visit_NodeBinaryArithmeticOperation(self)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(left={self.left}, operator={self.operator}, right={self.right})"


class NodeUnaryArithmeticOperation(NodeArithmeticExpression):
    __slots__ = ("operator", "operand")

    def __init__(self, operator: str, operand: NodeArithmeticExpression) -> None:
        self.operator: str = operator
        self.operand: NodeArithmeticExpression = operand

    def accept(self, visitor: NodeVisitor[T]) -> T:
        return visitor.visit_NodeUnaryArithmeticOperation(self)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(operator={self.operator}, operand={self.operand})"


class NodeArithmeticExpressionAsBoolean(NodeBooleanExpression):
    __slots__ = ("expression",)

    def __init__(self, expression: NodeArithmeticExpression) -> None:
        self.expression: NodeArithmeticExpression = expression

    def accept(self, visitor: NodeVisitor[T]) -> T:
        return visitor.visit_NodeArithmeticExpressionAsBoolean(self)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(expression={self.expression})"


class NodeBinaryBooleanOperation(NodeBooleanExpression):
    __slots__ = ("left", "logical_operator", "right")

    def __init__(
        self,
        left: NodeBooleanExpression,
        logical_operator: str,
        right: NodeBooleanExpression,
    ) -> None:
        self.left: NodeBooleanExpression = left
        self.logical_operator: str = logical_operator
        self.right: NodeBooleanExpression = right

    def accept(self, visitor: NodeVisitor[T]) -> T:
        return visitor.visit_NodeBinaryBooleanOperation(self)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(left={self.left}, logical_operator={self.logical_operator}, right={self.right})"


class NodeUnaryBooleanOperation(NodeBooleanExpression):
    __slots__ = ("logical_operator", "operand")

    def __init__(self, logical_operator: str, operand: NodeBooleanExpression) -> None:
        self.logical_operator: str = logical_operator
        self.operand: NodeBooleanExpression = operand

    def accept(self, visitor: NodeVisitor[T]) -> T:
        return visitor.visit_NodeUnaryBooleanOperation(self)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(logical_operator={self.logical_operator}, operand={self.operand})"


class NodeComparisonExpression(NodeBooleanExpression):
    __slots__ = ("left", "comparator", "right")

    def __init__(
        self,
        left: NodeArithmeticExpression,
        comparator: str,
        right: NodeArithmeticExpression,
    ) -> None:
        self.left: NodeArithmeticExpression = left
        self.comparator: str = comparator
        self.right: NodeArithmeticExpression = right

    def accept(self, visitor: NodeVisitor[T]) -> T:
        return visitor.visit_NodeComparisonExpression(self)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(left={self.left}, comparator={self.comparator}, right={self.right})"


class NodeNumberLiteral(NodeArithmeticExpression):
    __slots__ = ("lexeme",)

    def __init__(self, lexeme: str) -> None:
        self.lexeme: str = lexeme

    def accept(self, visitor: NodeVisitor[T]) -> T:
        return visitor.visit_NodeNumberLiteral(self)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(lexeme={self.lexeme})"


class NodeStringLiteral(NodeArithmeticExpression):
    __slots__ = ("lexeme",)

    def __init__(self, lexeme: str) -> None:
        self.lexeme: str = lexeme

    def accept(self, visitor: NodeVisitor[T]) -> T:
        return visitor.visit_NodeStringLiteral(self)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(lexeme={self.lexeme!r})"


class NodeBooleanLiteral(NodeBooleanExpression):
    __slots__ = ("lexeme",)

    def __init__(self, lexeme: str) -> None:
        self.lexeme: str = lexeme

    def accept(self, visitor: NodeVisitor[T]) -> T:
        return visitor.visit_NodeBooleanLiteral(self)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(lexeme={self.lexeme})"
