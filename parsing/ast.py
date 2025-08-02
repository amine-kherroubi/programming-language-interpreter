from typing import Union
from abc import ABC, abstractmethod
from lexical_analysis.tokens import Token, TokenType

ValueType = Union[int, float, str]


class NodeAST(ABC):
    __slots__ = ()

    @abstractmethod
    def __repr__(self) -> str:
        pass


class NodeVariable(NodeAST):
    __slots__ = ("id",)

    def __init__(self, token: Token) -> None:
        self.id: str = token.value

    def __repr__(self) -> str:
        return f"NodeVariable(id={self.id})"


class NodeType(NodeAST):
    __slots__ = ("type",)

    def __init__(self, token: Token) -> None:
        self.type: TokenType = token.type

    def __repr__(self) -> str:
        return f"NodeType(type={self.type})"


class NodeVariableDeclaration(NodeAST):
    __slots__ = ("variables", "type")

    def __init__(self, variables: list[NodeVariable], node_type: NodeType) -> None:
        self.variables: list[NodeVariable] = variables
        self.type: NodeType = node_type

    def __repr__(self) -> str:
        return f"NodeVariableDeclaration(variables={self.variables}, type={self.type})"


class NodeDeclarations(NodeAST):
    __slots__ = ("declarations",)

    def __init__(self, declarations: list[NodeVariableDeclaration]) -> None:
        self.declarations: list[NodeVariableDeclaration] = declarations

    def __repr__(self) -> str:
        return f"NodeDeclarations(declarations={self.declarations})"


class NodeEmpty(NodeAST):
    __slots__ = ()

    def __repr__(self) -> str:
        return "NodeEmpty()"


class NodeAssignmentStatement(NodeAST):
    __slots__ = ("left", "right")

    def __init__(self, left: NodeVariable, right: NodeAST) -> None:
        self.left: NodeVariable = left
        self.right: NodeAST = right

    def __repr__(self) -> str:
        return f"NodeAssignmentStatement(left={self.left}, right={self.right})"


class NodeCompoundStatement(NodeAST):
    __slots__ = ("children",)

    def __init__(
        self,
        children: list[
            Union["NodeCompoundStatement", NodeAssignmentStatement, NodeEmpty]
        ],
    ) -> None:
        self.children: list[
            Union[NodeCompoundStatement, NodeAssignmentStatement, NodeEmpty]
        ] = children

    def __repr__(self) -> str:
        return f"NodeCompoundStatement(children={self.children})"


class NodeBinaryOperation(NodeAST):
    __slots__ = ("left", "right", "operator")

    def __init__(self, left: NodeAST, token: Token, right: NodeAST) -> None:
        self.left: NodeAST = left
        self.right: NodeAST = right
        self.operator: str = token.value

    def __repr__(self) -> str:
        return f"NodeBinaryOperation(left={self.left}, operator={self.operator}, right={self.right})"


class NodeUnaryOperation(NodeAST):
    __slots__ = ("operator", "operand")

    def __init__(self, token: Token, operand: NodeAST) -> None:
        self.operator: str = token.value
        self.operand: NodeAST = operand

    def __repr__(self) -> str:
        return f"NodeUnaryOperation(operator={self.operator}, operand={self.operand})"


class NodeNumber(NodeAST):
    __slots__ = ("value",)

    def __init__(self, token: Token) -> None:
        self.value: Union[int, float] = token.value

    def __repr__(self) -> str:
        return f"NodeNumber(value={self.value})"


class NodeProgram(NodeAST):
    __slots__ = ("program_name", "variable_declaration_section", "main_block")

    def __init__(
        self,
        program_name: str,
        variable_declaration_section: Union[NodeDeclarations, NodeEmpty],
        main_block: NodeCompoundStatement,
    ) -> None:
        self.program_name: str = program_name
        self.variable_declaration_section: Union[NodeDeclarations, NodeEmpty] = (
            variable_declaration_section
        )
        self.main_block: NodeCompoundStatement = main_block

    def __repr__(self) -> str:
        return f"NodeProgram(program_name={self.program_name}, variable_declaration_section={self.variable_declaration_section}, main_block={self.main_block})"
