from typing import Optional, Union
from abc import ABC, abstractmethod
from lexical_analysis.tokens import Token

# Only supporting wholes and reals for now
NumericType = Union[int, float]


class NodeAST(ABC):
    __slots__ = ()

    @abstractmethod
    def __repr__(self) -> str:
        pass


class NodeStatement(NodeAST):
    pass


class NodeExpression(NodeAST):
    pass


class NodeBlock(NodeAST):
    __slots__ = ("statements",)

    def __init__(self, statements: list[NodeStatement]) -> None:
        self.statements: list[NodeStatement] = statements

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


# For identifier references in expressions
class NodeIdentifier(NodeExpression):
    __slots__ = ("identifier",)

    def __init__(self, identifier: str) -> None:
        self.identifier: str = identifier

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(identifier={self.identifier})"


class NodeSameTypeVariableDeclarationGroup(NodeAST):
    __slots__ = ("identifier_group", "type", "expression_group")

    def __init__(
        self,
        identifier_group: list[NodeIdentifier],
        node_type: NodeType,
        expression_group: Optional[list[NodeExpression]],  # Optional initialization
    ) -> None:
        self.identifier_group: list[NodeIdentifier] = identifier_group
        self.type: NodeType = node_type
        self.expression_group: Optional[list[NodeExpression]] = expression_group

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(identifier_group={self.identifier_group}, type={self.type}, expression_group={self.expression_group})"


class NodeSameTypeConstantDeclarationGroup(NodeAST):
    __slots__ = ("identifier_group", "type", "expression_group")

    def __init__(
        self,
        identifier_group: list[NodeIdentifier],
        node_type: NodeType,
        expression_group: list[NodeExpression],  # Constants must be initialized
    ) -> None:
        self.identifier_group: list[NodeIdentifier] = identifier_group
        self.type: NodeType = node_type
        self.expression_group: list[NodeExpression] = expression_group

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(identifier_group={self.identifier_group}, type={self.type}, expression_group={self.expression_group})"


class NodeVariableDeclaration(NodeStatement):
    __slots__ = ("same_type_groups",)

    def __init__(
        self, same_type_groups: list[NodeSameTypeVariableDeclarationGroup]
    ) -> None:
        self.same_type_groups: list[NodeSameTypeVariableDeclarationGroup] = (
            same_type_groups
        )

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(same_type_groups={self.same_type_groups})"


class NodeConstantDeclaration(NodeStatement):
    __slots__ = ("same_type_groups",)

    def __init__(
        self, same_type_groups: list[NodeSameTypeConstantDeclarationGroup]
    ) -> None:
        self.same_type_groups: list[NodeSameTypeConstantDeclarationGroup] = (
            same_type_groups
        )

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(same_type_groups={self.same_type_groups})"


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


class NodeParameter(NodeAST):
    __slots__ = ("identifier", "type")

    def __init__(self, identifier: NodeIdentifier, type: NodeType) -> None:
        self.identifier: NodeIdentifier = identifier
        self.type: NodeType = type

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}(identifier={self.identifier}, type={self.type})"
        )


class NodeUnit(NodeExpression):
    __slots__ = ("parameters", "type", "block")

    def __init__(
        self,
        parameters: Optional[list[NodeParameter]],
        type: Optional[NodeType],
        block: NodeBlock,
    ) -> None:
        self.parameters: Optional[list[NodeParameter]] = parameters
        self.type: Optional[NodeType] = type
        self.block: NodeBlock = block

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(parameters={self.parameters}, type={self.type}, block={self.block})"


class NodeUnitUse(NodeStatement, NodeExpression):
    __slots__ = ("identifier", "arguments")

    def __init__(
        self, identifier: str, arguments: Optional[list[NodeExpression]]
    ) -> None:
        self.identifier: str = identifier
        self.arguments: Optional[list[NodeExpression]] = arguments

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(identifier={self.identifier}, arguments={self.arguments})"


class NodeBinaryOperation(NodeExpression):
    __slots__ = ("left_expression", "operator", "right_expression")

    def __init__(
        self,
        left_expression: NodeExpression,
        operator: str,
        right_expression: NodeExpression,
    ) -> None:
        self.left_expression: NodeExpression = left_expression
        self.operator: str = operator
        self.right_expression: NodeExpression = right_expression

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(left_expression={self.left_expression}, operator={self.operator}, right_expression={self.right_expression})"


class NodeUnaryOperation(NodeExpression):
    __slots__ = ("operator", "expression")

    def __init__(self, operator: str, expression: NodeExpression) -> None:
        self.operator: str = operator
        self.expression: NodeExpression = expression

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(operator={self.operator}, expression={self.expression})"


class NodeNumericLiteral(NodeExpression):
    __slots__ = ("value",)

    def __init__(self, value: NumericType) -> None:
        self.value: NumericType = value

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(value={self.value})"
