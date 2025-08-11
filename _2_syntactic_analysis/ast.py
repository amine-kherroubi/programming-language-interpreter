from abc import ABC, abstractmethod
from typing import Optional, Union
from _1_lexical_analysis.tokens import Token

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


class NodeArithmeticExpression(NodeExpression):
    __slots__ = ()


class NodeBooleanExpression(NodeExpression):
    __slots__ = ()


class NodeBlock(NodeAST):
    __slots__ = ("statements",)

    def __init__(self, statements: Optional[list[NodeStatement]]) -> None:
        self.statements: Optional[list[NodeStatement]] = statements

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(statements={self.statements})"


class NodeProgram(NodeAST):
    __slots__ = ("block",)

    def __init__(self, block: NodeBlock) -> None:
        self.block: NodeBlock = block

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(block={self.block})"


class NodeType(NodeAST):
    __slots__ = ("name",)

    def __init__(self, token: Token) -> None:
        self.name: str = token.type.value

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name={self.name})"


class NodeIdentifier(NodeArithmeticExpression):
    __slots__ = ("name",)

    def __init__(self, name: str) -> None:
        self.name: str = name

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
        self.type: NodeType = var_type
        self.identifiers: list[NodeIdentifier] = identifiers
        self.expressions: Optional[list[NodeExpression]] = expressions

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

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(identifier={self.identifier}, expression={self.expression})"


class NodeGiveStatement(NodeStatement):
    __slots__ = ("expression",)

    def __init__(self, expression: Optional[NodeExpression]) -> None:
        self.expression: Optional[NodeExpression] = expression

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(expression={self.expression})"


class NodeShowStatement(NodeStatement):
    __slots__ = ("expression",)

    def __init__(self, expression: NodeExpression) -> None:
        self.expression: NodeExpression = expression

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

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(block={self.block})"


class NodeIfStatement(NodeStatement):
    __slots__ = ("condition", "block", "elifs", "else_")

    def __init__(
        self,
        condition: NodeBooleanExpression,
        block: NodeBlock,
        elifs: Optional[list[NodeElif]],
        else_: Optional[NodeElse],
    ) -> None:
        self.condition: NodeBooleanExpression = condition
        self.block: NodeBlock = block
        self.elifs: Optional[list[NodeElif]] = elifs
        self.else_: Optional[NodeElse] = else_

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

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}(condition={self.condition}, block={self.block})"
        )


class NodeSkipStatement(NodeStatement):
    __slots__ = ()

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}()"


class NodeStopStatement(NodeStatement):
    __slots__ = ()

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}()"


class NodeParameter(NodeAST):
    __slots__ = ("identifier", "type")

    def __init__(self, identifier: NodeIdentifier, type: NodeType) -> None:
        self.identifier: NodeIdentifier = identifier
        self.type: NodeType = type

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
        self.identifier: NodeIdentifier = identifier
        self.parameters: Optional[list[NodeParameter]] = parameters
        self.give_type: NodeType = give_type
        self.block: NodeBlock = block

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
        self.identifier: NodeIdentifier = identifier
        self.parameters: Optional[list[NodeParameter]] = parameters
        self.block: NodeBlock = block

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(identifier={self.identifier}, parameters={self.parameters}, block={self.block})"


class NodeFunctionCall(NodeArithmeticExpression):
    __slots__ = ("identifier", "arguments")

    def __init__(
        self,
        identifier: NodeIdentifier,
        arguments: Optional[list[NodeExpression]],
    ) -> None:
        self.identifier: NodeIdentifier = identifier
        self.arguments: Optional[list[NodeExpression]] = arguments

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(identifier={self.identifier}, arguments={self.arguments})"


class NodeProcedureCall(NodeStatement):
    __slots__ = ("identifier", "arguments")

    def __init__(
        self,
        identifier: NodeIdentifier,
        arguments: Optional[list[NodeExpression]],
    ) -> None:
        self.identifier: NodeIdentifier = identifier
        self.arguments: Optional[list[NodeExpression]] = arguments

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

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(left={self.left}, operator={self.operator}, right={self.right})"


class NodeUnaryArithmeticOperation(NodeArithmeticExpression):
    __slots__ = ("operator", "operand")

    def __init__(self, operator: str, operand: NodeArithmeticExpression) -> None:
        self.operator: str = operator
        self.operand: NodeArithmeticExpression = operand

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(operator={self.operator}, operand={self.operand})"


class NodeArithmeticExpressionAsBoolean(NodeBooleanExpression):
    __slots__ = ("expression",)

    def __init__(self, expression: NodeArithmeticExpression) -> None:
        self.expression: NodeArithmeticExpression = expression

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

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(left={self.left}, logical_operator={self.logical_operator}, right={self.right})"


class NodeUnaryBooleanOperation(NodeBooleanExpression):
    __slots__ = ("logical_operator", "operand")

    def __init__(self, logical_operator: str, operand: NodeBooleanExpression) -> None:
        self.logical_operator: str = logical_operator
        self.operand: NodeBooleanExpression = operand

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

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(left={self.left}, comparator={self.comparator}, right={self.right})"


class NodeNumberLiteral(NodeArithmeticExpression):
    __slots__ = ("value",)

    def __init__(self, value: int) -> None:
        self.value: int = value

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(value={self.value})"


class NodeStringLiteral(NodeArithmeticExpression):
    __slots__ = ("value",)

    def __init__(self, value: str) -> None:
        self.value: str = value

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(value={self.value!r})"


class NodeBooleanLiteral(NodeBooleanExpression):
    __slots__ = ("value",)

    def __init__(self, value: bool) -> None:
        self.value: bool = value

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(value={self.value})"
