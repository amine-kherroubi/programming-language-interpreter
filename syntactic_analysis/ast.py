from typing import Union
from abc import ABC, abstractmethod
from lexical_analysis.tokens import Token

ValueType = Union[int, float, str]
NumericType = Union[int, float]


class NodeAST(ABC):
    __slots__ = ()

    @abstractmethod
    def __repr__(self) -> str:
        pass


class NodeVariable(NodeAST):
    __slots__ = ("name",)

    def __init__(self, token: Token) -> None:
        self.name: str = token.value

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name={self.name})"


class NodeType(NodeAST):
    __slots__ = ("name",)

    def __init__(self, token: Token) -> None:
        self.name: str = token.type.name

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name={self.name})"


class NodeVariableDeclarationGroup(NodeAST):
    __slots__ = ("members", "type")

    def __init__(self, members: list[NodeVariable], node_type: NodeType) -> None:
        self.members: list[NodeVariable] = members
        self.type: NodeType = node_type

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(members={self.members}, type={self.type})"


class NodeVariableDeclarations(NodeAST):
    __slots__ = ("variable_declarations",)

    def __init__(
        self, variable_declarations: list[NodeVariableDeclarationGroup]
    ) -> None:
        self.variable_declarations: list[NodeVariableDeclarationGroup] = (
            variable_declarations
        )

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(variable_declarations={self.variable_declarations})"


class NodeEmpty(NodeAST):
    __slots__ = ()

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}()"


class NodeAssignmentStatement(NodeAST):
    __slots__ = ("left", "right")

    def __init__(self, left: NodeVariable, right: NodeAST) -> None:
        self.left: NodeVariable = left
        self.right: NodeAST = right

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(left={self.left}, right={self.right})"


class NodeCompoundStatement(NodeAST):
    __slots__ = ("children",)

    def __init__(
        self,
        children: list[
            Union[
                "NodeCompoundStatement",
                "NodeProcedureCall",
                NodeAssignmentStatement,
                NodeEmpty,
            ]
        ],
    ) -> None:
        self.children: list[
            Union[
                NodeCompoundStatement,
                NodeProcedureCall,
                NodeAssignmentStatement,
                NodeEmpty,
            ]
        ] = children

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(children={self.children})"


class NodeBinaryOperation(NodeAST):
    __slots__ = ("left", "right", "operator")

    def __init__(self, left: NodeAST, token: Token, right: NodeAST) -> None:
        self.left: NodeAST = left
        self.right: NodeAST = right
        self.operator: str = token.value

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(left={self.left}, operator={self.operator}, right={self.right})"


class NodeUnaryOperation(NodeAST):
    __slots__ = ("operator", "operand")

    def __init__(self, token: Token, operand: NodeAST) -> None:
        self.operator: str = token.value
        self.operand: NodeAST = operand

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(operator={self.operator}, operand={self.operand})"


class NodeNumber(NodeAST):
    __slots__ = ("value",)

    def __init__(self, token: Token) -> None:
        self.value: NumericType = token.value

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(value={self.value})"


class NodeBlock(NodeAST):
    __slots__ = (
        "variable_declarations",
        "subroutine_declarations",
        "compound_statement",
    )

    def __init__(
        self,
        variable_declarations: Union[NodeVariableDeclarations, NodeEmpty],
        subroutine_declarations: Union["NodeSubroutineDeclarations", NodeEmpty],
        compound_statement: NodeCompoundStatement,
    ) -> None:
        self.variable_declarations: Union[NodeVariableDeclarations, NodeEmpty] = (
            variable_declarations
        )
        self.subroutine_declarations: Union[NodeSubroutineDeclarations, NodeEmpty] = (
            subroutine_declarations
        )
        self.compound_statement: NodeCompoundStatement = compound_statement

    def __repr__(self) -> str:
        return "{}(variable_declarations={}, subroutine_declarations={}, compound_statement={})".format(
            self.__class__.__name__,
            self.variable_declarations,
            self.subroutine_declarations,
            self.compound_statement,
        )


class NodeParameterGroup(NodeAST):
    __slots__ = ("members", "type")

    def __init__(self, members: list[NodeVariable], type: NodeType) -> None:
        self.members: list[NodeVariable] = members
        self.type: NodeType = type

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(members={self.members}, type={self.type})"


class NodeProcedureDeclaration(NodeAST):
    __slots__ = ("name", "parameters", "block")

    def __init__(
        self,
        name: str,
        parameters: Union[NodeEmpty, list[NodeParameterGroup]],
        block: NodeBlock,
    ) -> None:
        self.name: str = name
        self.parameters: Union[NodeEmpty, list[NodeParameterGroup]] = parameters
        self.block: NodeBlock = block

    def __repr__(self) -> str:
        return "{}(name={}, parameters={}, block={})".format(
            self.__class__.__name__, self.name, self.parameters, self.block
        )


class NodeFunctionDeclaration(NodeAST):
    __slots__ = ("name", "parameters", "type", "block")

    def __init__(
        self,
        name: str,
        parameters: Union[NodeEmpty, list[NodeParameterGroup]],
        type: NodeType,
        block: NodeBlock,
    ) -> None:
        self.name: str = name
        self.parameters: Union[NodeEmpty, list[NodeParameterGroup]] = parameters
        self.type: NodeType = type
        self.block: NodeBlock = block

    def __repr__(self) -> str:
        return "{}(name={}, parameters={}, type={}, block={})".format(
            self.__class__.__name__, self.name, self.parameters, self.type, self.block
        )


class NodeSubroutineDeclarations(NodeAST):
    __slots__ = ("declarations",)

    def __init__(
        self,
        declarations: list[Union[NodeProcedureDeclaration, NodeFunctionDeclaration]],
    ) -> None:
        self.declarations: list[
            Union[NodeProcedureDeclaration, NodeFunctionDeclaration]
        ] = declarations

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(declarations={self.declarations})"


class NodeProcedureCall(NodeAST):
    __slots__ = (
        "name",
        "arguments",
    )

    def __init__(self, name: str, arguments: Union[NodeEmpty, list[NodeAST]]) -> None:
        self.name: str = name
        self.arguments: Union[NodeEmpty, list[NodeAST]] = arguments
        pass

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}(name={self.name}, arguments={self.arguments})"
        )


class NodeProgram(NodeAST):
    __slots__ = ("name", "block")

    def __init__(self, name: str, block: NodeBlock) -> None:
        self.name: str = name
        self.block: NodeBlock = block

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name={self.name}, block={self.block})"
