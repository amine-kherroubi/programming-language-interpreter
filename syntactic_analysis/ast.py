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


class NodeArithmeticExpression(NodeAST):
    __slots__ = ()


class NodeBooleanExpression(NodeAST):
    __slots__ = ()


class NodeArithmeticExpressionAsBoolean(NodeBooleanExpression):
    __slots__ = ("expression",)

    def __init__(self, expression: NodeArithmeticExpression) -> None:
        self.expression = expression

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(expression={self.expression})"


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


class NodeIdentifier(NodeArithmeticExpression):
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
        expressions: Optional[list[NodeArithmeticExpression]] = None,
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
        expressions: list[NodeArithmeticExpression],
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

    def __init__(
        self, identifier: NodeIdentifier, expression: NodeArithmeticExpression
    ) -> None:
        self.identifier = identifier
        self.expression = expression

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(identifier={self.identifier}, expression={self.expression})"


class NodeGiveStatement(NodeStatement):
    __slots__ = ("expression",)

    def __init__(self, expression: Optional[NodeArithmeticExpression]) -> None:
        self.expression = expression

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(expression={self.expression})"


class NodeShowStatement(NodeStatement):
    __slots__ = ("expression",)

    def __init__(self, expression: Optional[NodeArithmeticExpression]) -> None:
        self.expression = expression

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(expression={self.expression})"


class NodeSkipStatement(NodeStatement):
    __slots__ = ()

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}()"


class NodeStopStatement(NodeStatement):
    __slots__ = ()

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}()"


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


class NodeFunctionCall(NodeArithmeticExpression):
    __slots__ = ("identifier", "arguments")

    def __init__(
        self,
        identifier: NodeIdentifier,
        arguments: Optional[list[NodeArithmeticExpression]],
    ) -> None:
        self.identifier = identifier
        self.arguments = arguments

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(identifier={self.identifier}, arguments={self.arguments})"


class NodeProcedureCall(NodeStatement):
    __slots__ = ("identifier", "arguments")

    def __init__(
        self,
        identifier: NodeIdentifier,
        arguments: Optional[list[NodeArithmeticExpression]],
    ) -> None:
        self.identifier = identifier
        self.arguments = arguments

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(identifier={self.identifier}, arguments={self.arguments})"


class NodeBinaryOperation(NodeArithmeticExpression):
    __slots__ = ("left", "operator", "right")

    def __init__(
        self,
        left: NodeArithmeticExpression,
        operator: str,
        right: NodeArithmeticExpression,
    ) -> None:
        self.left = left
        self.operator = operator
        self.right = right

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(left={self.left}, operator={self.operator}, right={self.right})"


class NodeUnaryOperation(NodeArithmeticExpression):
    __slots__ = ("operator", "operand")

    def __init__(self, operator: str, operand: NodeArithmeticExpression) -> None:
        self.operator = operator
        self.operand = operand

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(operator={self.operator}, operand={self.operand})"


class NodeBinaryBooleanOperation(NodeBooleanExpression):
    __slots__ = ("left", "logical_operator", "right")

    def __init__(
        self,
        left: NodeBooleanExpression,
        logical_operator: str,
        right: NodeBooleanExpression,
    ) -> None:
        self.left = left
        self.logical_operator = logical_operator
        self.right = right

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(left={self.left}, logical_operator={self.logical_operator}, right={self.right})"


class NodeUnaryBooleanOperation(NodeBooleanExpression):
    __slots__ = ("logical_operator", "operand")

    def __init__(self, logical_operator: str, operand: NodeBooleanExpression) -> None:
        self.logical_operator = logical_operator
        self.operand = operand

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(logical_operator={self.logical_operator}, operand={self.operand})"


class NodeComparison(NodeBooleanExpression):
    __slots__ = ("left", "comparator", "right")

    def __init__(
        self,
        left: NodeArithmeticExpression,
        comparator: str,
        right: NodeArithmeticExpression,
    ) -> None:
        self.left = left
        self.comparator = comparator
        self.right = right

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(left={self.left}, comparator={self.comparator}, right={self.right})"


class NodeIntegerLiteral(NodeArithmeticExpression):
    __slots__ = ("value",)

    def __init__(self, value: int) -> None:
        self.value: int = value

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(value={self.value})"


class NodeFloatLiteral(NodeArithmeticExpression):
    __slots__ = ("value",)

    def __init__(self, value: float) -> None:
        self.value: float = value

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(value={self.value})"


class NodeStringLiteral(NodeArithmeticExpression):
    __slots__ = ("value",)

    def __init__(self, value: str) -> None:
        self.value: str = value

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(value={self.value!r})"


class NodeBooleanLiteral(NodeArithmeticExpression):
    __slots__ = ("value",)

    def __init__(self, value: bool) -> None:
        self.value: bool = value

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(value={self.value})"
