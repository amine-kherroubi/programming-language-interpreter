from abc import ABC, abstractmethod
from typing import Optional, Union
from lexical_analysis.tokens import Token

NumericType = Union[int, float]


class NodeAST(ABC):
    __slots__ = ()

    @abstractmethod
    def __repr__(self) -> str:
        pass


class NodeStatement(NodeAST):
    __slots__ = ()


class NodeExpression(NodeAST):
    __slots__ = ()


class NodeBlock(NodeAST):
    __slots__ = ("statements",)

    def __init__(self, statements: list[NodeStatement]) -> None:
        self.statements = statements

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(statements={self.statements})"


class NodeProgram(NodeAST):
    __slots__ = ("block",)

    def __init__(self, block: NodeBlock) -> None:
        self.block = block

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(block={self.block})"


class NodeType(NodeAST):
    __slots__ = ("name",)

    def __init__(self, token: Token) -> None:
        self.name = token.type.value

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name={self.name})"


class NodeIdentifier(NodeExpression):
    __slots__ = ("name",)

    def __init__(self, name: str) -> None:
        self.name = name

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name={self.name})"


class NodeVariableDeclaration(NodeStatement):
    __slots__ = ("type", "identifiers", "expressions")

    def __init__(
        self,
        var_type: NodeType,
        identifiers: list[NodeIdentifier],
        expressions: Optional[list[NodeExpression]] = None,
    ) -> None:
        self.type = var_type
        self.identifiers = identifiers
        self.expressions = expressions

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
        self.type = const_type
        self.identifiers = identifiers
        self.expressions = expressions

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}(type={self.type}, "
            f"identifiers={self.identifiers}, expressions={self.expressions})"
        )


class NodeAssignment(NodeStatement):
    __slots__ = ("identifier", "expression")

    def __init__(self, identifier: NodeIdentifier, expression: NodeExpression) -> None:
        self.identifier = identifier
        self.expression = expression

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(identifier={self.identifier}, expression={self.expression})"


class NodeGiveStatement(NodeStatement):
    __slots__ = ("expression",)

    def __init__(self, expression: Optional[NodeExpression]) -> None:
        self.expression = expression

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(expression={self.expression})"


class NodeParameter(NodeAST):
    __slots__ = ("identifier", "type")

    def __init__(self, identifier: NodeIdentifier, param_type: NodeType) -> None:
        self.identifier = identifier
        self.type = param_type

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}(identifier={self.identifier}, type={self.type})"
        )


class NodeFunctionDeclaration(NodeStatement):
    __slots__ = ("identifier", "parameters", "give_type", "block")

    def __init__(
        self,
        identifier: NodeIdentifier,
        parameters: Optional[list[NodeParameter]],
        give_type: NodeType,
        block: NodeBlock,
    ) -> None:
        self.identifier = identifier
        self.parameters = parameters
        self.give_type = give_type
        self.block = block

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
        parameters: Optional[list[NodeParameter]],
        block: NodeBlock,
    ) -> None:
        self.identifier = identifier
        self.parameters = parameters
        self.block = block

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(identifier={self.identifier}, parameters={self.parameters}, block={self.block})"


class NodeFunctionCall(NodeExpression):
    __slots__ = ("identifier", "arguments")

    def __init__(
        self, identifier: NodeIdentifier, arguments: Optional[list[NodeExpression]]
    ) -> None:
        self.identifier = identifier
        self.arguments = arguments

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(identifier={self.identifier}, arguments={self.arguments})"


class NodeProcedureCall(NodeStatement):
    __slots__ = ("identifier", "arguments")

    def __init__(
        self, identifier: NodeIdentifier, arguments: Optional[list[NodeExpression]]
    ) -> None:
        self.identifier = identifier
        self.arguments = arguments

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(identifier={self.identifier}, arguments={self.arguments})"


class NodeBinaryOperation(NodeExpression):
    __slots__ = ("left", "operator", "right")

    def __init__(
        self, left: NodeExpression, operator: str, right: NodeExpression
    ) -> None:
        self.left = left
        self.operator = operator
        self.right = right

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(left={self.left}, operator={self.operator}, right={self.right})"


class NodeUnaryOperation(NodeExpression):
    __slots__ = ("operator", "operand")

    def __init__(self, operator: str, operand: NodeExpression) -> None:
        self.operator = operator
        self.operand = operand

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(operator={self.operator}, operand={self.operand})"


class NodeIntegerLiteral(NodeExpression):
    __slots__ = ("value",)

    def __init__(self, value: int) -> None:
        self.value: int = value

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(value={self.value})"


class NodeFloatLiteral(NodeExpression):
    __slots__ = ("value",)

    def __init__(self, value: float) -> None:
        self.value: float = value

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(value={self.value})"


class NodeStringLiteral(NodeExpression):
    __slots__ = ("value",)

    def __init__(self, value: str) -> None:
        self.value: str = value

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(value={self.value!r})"


class NodeBooleanLiteral(NodeExpression):
    __slots__ = ("value",)

    def __init__(self, value: bool) -> None:
        self.value: bool = value

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(value={self.value})"
