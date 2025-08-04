from typing import Union
from abc import ABC, abstractmethod
from lexical_analysis.tokens import Token

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
        self.type: str = token.type.name

    def __repr__(self) -> str:
        return f"NodeType(type={self.type})"


class NodeVariableDeclaration(NodeAST):
    __slots__ = ("variables", "type")

    def __init__(self, variables: list[NodeVariable], node_type: NodeType) -> None:
        self.variables: list[NodeVariable] = variables
        self.type: NodeType = node_type

    def __repr__(self) -> str:
        return f"NodeVariableDeclaration(variables={self.variables}, type={self.type})"


class NodeVariableDeclarations(NodeAST):
    __slots__ = ("variable_declarations",)

    def __init__(self, variable_declarations: list[NodeVariableDeclaration]) -> None:
        self.variable_declarations: list[NodeVariableDeclaration] = (
            variable_declarations
        )

    def __repr__(self) -> str:
        return f"NodeVariableDeclarations(variable_declarations={self.variable_declarations})"


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
        return f"NodeBlock(variable_declarations={self.variable_declarations}, compound_statement={self.compound_statement})"


class NodeParameterGroup(NodeAST):
    __slots__ = ("parameters", "type")

    def __init__(self, parameter: list[NodeVariable], type: NodeType) -> None:
        self.parameters: list[NodeVariable] = parameter
        self.type: NodeType = type

    def __repr__(self) -> str:
        return f"NodeParameterGroup(parameter={self.parameters}, type={self.type})"


class NodeProcedureDeclaration(NodeAST):
    __slots__ = ("procedure_name", "parameters", "block")

    def __init__(
        self,
        procedure_name: str,
        parameters: Union[NodeEmpty, list[NodeParameterGroup]],
        block: NodeBlock,
    ) -> None:
        self.procedure_name: str = procedure_name
        self.parameters: Union[NodeEmpty, list[NodeParameterGroup]] = parameters
        self.block: NodeBlock = block

    def __repr__(self) -> str:
        return "NodeProcedureDeclaration(procedure_name={}, parameters={}, block={})".format(
            self.procedure_name, self.parameters, self.block
        )


class NodeFunctionDeclaration(NodeAST):
    __slots__ = ("function_name", "parameters", "return_type", "block")

    def __init__(
        self,
        function_name: str,
        parameters: Union[NodeEmpty, list[NodeParameterGroup]],
        return_type: NodeType,
        block: NodeBlock,
    ) -> None:
        self.function_name: str = function_name
        self.parameters: Union[NodeEmpty, list[NodeParameterGroup]] = parameters
        self.return_type: NodeType = return_type
        self.block: NodeBlock = block

    def __repr__(self) -> str:
        return "NodeFunctionDeclaration(function_name={}, parameters={}, return_type= {}, block={})".format(
            self.function_name, self.parameters, self.return_type, self.block
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
        return f"NodeSubroutineDeclarations(declarations={self.declarations})"


class NodeProgram(NodeAST):
    __slots__ = ("program_name", "main_block")

    def __init__(self, program_name: str, main_block: NodeBlock) -> None:
        self.program_name: str = program_name
        self.main_block: NodeBlock = main_block

    def __repr__(self) -> str:
        return f"NodeProgram(program_name={self.program_name}, main_block={self.main_block})"
