from enum import Enum
from typing import Optional, Union
from abc import ABC, abstractmethod
from lexical_analysis.tokens import Token

NumericType = Union[int, float]


class TruthType(Enum):
    true = 1
    false = 0


class NodeAST(ABC):
    __slots__ = ()

    @abstractmethod
    def __repr__(self) -> str:
        pass


class NodeStatement(NodeAST):
    pass


class NodeAssignable(NodeAST):
    pass


class NodeExpression(NodeAssignable):
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


class NodeIdentifier(NodeExpression):
    __slots__ = ("name",)

    def __init__(self, name: str) -> None:
        self.name: str = name

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name={self.name})"


class NodeSameTypeVariableDeclarationGroup(NodeAST):
    __slots__ = ("identifier_group", "type", "assignable_group")

    def __init__(
        self,
        identifier_group: list[NodeIdentifier],
        node_type: NodeType,
        assignable_group: Optional[list[NodeAssignable]],
    ) -> None:
        self.identifier_group: list[NodeIdentifier] = identifier_group
        self.type: NodeType = node_type
        self.assignable_group: Optional[list[NodeAssignable]] = assignable_group

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(identifier_group={self.identifier_group}, type={self.type}, assignable_group={self.assignable_group})"


class NodeSameTypeConstantDeclarationGroup(NodeAST):
    __slots__ = ("identifier_group", "type", "assignable_group")

    def __init__(
        self,
        identifier_group: list[NodeIdentifier],
        node_type: NodeType,
        assignable_group: list[NodeAssignable],
    ) -> None:
        self.identifier_group: list[NodeIdentifier] = identifier_group
        self.type: NodeType = node_type
        self.assignable_group: list[NodeAssignable] = assignable_group

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(identifier_group={self.identifier_group}, type={self.type}, assignable_group={self.assignable_group})"


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


class NodeAssignment(NodeStatement):
    __slots__ = ("identifier", "assignable")

    def __init__(self, identifier: NodeIdentifier, assignable: NodeAssignable) -> None:
        self.identifier: NodeIdentifier = identifier
        self.assignable: NodeAssignable = assignable

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(identifier={self.identifier}, assignable={self.assignable})"


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


class NodeUnit(NodeAST):
    __slots__ = ("parameters", "block", "assigned_name")

    def __init__(
        self,
        parameters: Optional[list[NodeParameter]],
        block: NodeBlock,
    ) -> None:
        self.parameters: Optional[list[NodeParameter]] = parameters
        self.block: NodeBlock = block
        self.assigned_name: Optional[str] = None

    def set_assigned_name(self, name: str) -> None:
        self.assigned_name = name

    def is_anonymous(self) -> bool:
        return self.assigned_name is None


class NodeExpressionUnit(NodeUnit, NodeExpression):
    __slots__ = ("return_type",)

    def __init__(
        self,
        parameters: Optional[list[NodeParameter]],
        return_type: NodeType,
        block: NodeBlock,
    ) -> None:
        super().__init__(parameters, block)
        self.return_type: NodeType = return_type

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(parameters={self.parameters}, return_type={self.return_type}, block={self.block}, assigned_name={self.assigned_name})"


class NodeProcedureUnit(NodeUnit, NodeStatement, NodeAssignable):
    __slots__ = ()

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(parameters={self.parameters}, block={self.block}, assigned_name={self.assigned_name})"


from semantic_analysis.symbol_table import UnitSymbol


class NodeUnitUse(NodeStatement, NodeExpression):
    __slots__ = ("identifier", "arguments", "symbol")

    def __init__(
        self, identifier: str, arguments: Optional[list[NodeExpression]]
    ) -> None:
        self.identifier: NodeIdentifier = NodeIdentifier(identifier)
        self.arguments: Optional[list[NodeExpression]] = arguments
        self.symbol: Optional[UnitSymbol] = None

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


class NodeTextualLiteral(NodeExpression):
    __slots__ = ("value",)

    def __init__(self, value: str) -> None:
        self.value: str = value

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(value={self.value})"


class NodeTruthLiteral(NodeExpression):
    __slots__ = ("value",)

    def __init__(self, value: TruthType) -> None:
        self.value: TruthType = value

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(value={self.value})"
