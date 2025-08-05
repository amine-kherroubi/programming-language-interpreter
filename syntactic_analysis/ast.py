from typing import Union
from abc import ABC, abstractmethod
from lexical_analysis.tokens import Token

# Type aliases for values that can be stored in AST nodes
ValueType = Union[int, float, str]
NumericType = Union[int, float]


class NodeAST(ABC):
    """
    Abstract base class for all Abstract Syntax Tree (AST) nodes.

    This class defines the common interface that all AST nodes must implement.
    It uses __slots__ for memory efficiency and requires all subclasses to
    implement a __repr__ method for debugging and visualization purposes.

    All AST nodes represent different constructs in the parsed program:
    variables, expressions, statements, declarations, and program structure.
    """

    # Use __slots__ for memory efficiency - no additional attributes in base class
    __slots__ = ()

    @abstractmethod
    def __repr__(self) -> str:
        """Return a string representation of the AST node for debugging."""
        pass


class NodeVariable(NodeAST):
    """
    Represents a variable identifier in the AST.

    This node stores the name of a variable as it appears in the source code.
    Variables can be used in expressions, assignments, and declarations.
    """

    # Use __slots__ for memory efficiency - restricts instance attributes
    __slots__ = ("name",)

    def __init__(self, token: Token) -> None:
        """
        Initialize a variable node from a token.

        Args:
            token: Token containing the variable name as its value
        """
        self.name: str = token.value  # Variable name from source code

    def __repr__(self) -> str:
        """Return a string representation of the variable node."""
        return f"NodeVariable(name={self.name})"


class NodeType(NodeAST):
    """
    Represents a type identifier in the AST.

    This node stores type information for variable declarations and function
    return types. The type name is extracted from the token's type attribute.
    """

    # Use __slots__ for memory efficiency - restricts instance attributes
    __slots__ = ("name",)

    def __init__(self, token: Token) -> None:
        """
        Initialize a type node from a token.

        Args:
            token: Token whose type name will be used as the type identifier
        """
        self.name: str = token.type.name  # Type name from token type

    def __repr__(self) -> str:
        """Return a string representation of the type node."""
        return f"NodeType(name={self.name})"


class NodeVariableDeclarationGroup(NodeAST):
    """
    Represents a group of variables declared with the same type.

    In Pascal-like languages, multiple variables can be declared together:
    "var x, y, z: integer;" - this creates one declaration group with
    three variables all of type integer.
    """

    # Use __slots__ for memory efficiency - restricts instance attributes
    __slots__ = ("members", "type")

    def __init__(self, members: list[NodeVariable], node_type: NodeType) -> None:
        """
        Initialize a variable declaration group.

        Args:
            members: List of variables being declared together
            node_type: The type that all variables in this group share
        """
        self.members: list[NodeVariable] = (
            members  # Variables in this declaration group
        )
        self.type: NodeType = node_type  # Shared type for all variables

    def __repr__(self) -> str:
        """Return a string representation of the variable declaration group."""
        return f"NodeVariableDeclarationGroup(members={self.members}, type={self.type})"


class NodeVariableDeclarations(NodeAST):
    """
    Represents the complete variable declarations section of a program block.

    This node contains all variable declaration groups that appear in a
    VAR section. It serves as a container for organizing multiple
    declaration groups within a single program block.
    """

    # Use __slots__ for memory efficiency - restricts instance attributes
    __slots__ = ("variable_declarations",)

    def __init__(
        self, variable_declarations: list[NodeVariableDeclarationGroup]
    ) -> None:
        """
        Initialize the variable declarations container.

        Args:
            variable_declarations: List of all variable declaration groups
        """
        self.variable_declarations: list[NodeVariableDeclarationGroup] = (
            variable_declarations  # All declaration groups in this VAR section
        )

    def __repr__(self) -> str:
        """Return a string representation of the variable declarations."""
        return f"NodeVariableDeclarations(variable_declarations={self.variable_declarations})"


class NodeEmpty(NodeAST):
    """
    Represents an empty or null statement in the AST.

    This node is used for optional constructs that are not present,
    such as empty statement lists, missing variable declarations,
    or placeholder statements. It helps maintain consistent AST structure.
    """

    # Use __slots__ for memory efficiency - no additional attributes needed
    __slots__ = ()

    def __repr__(self) -> str:
        """Return a string representation of the empty node."""
        return "NodeEmpty()"


class NodeAssignmentStatement(NodeAST):
    """
    Represents an assignment statement in the AST.

    This node captures assignments like "x := 5" or "result := a + b".
    It contains the variable being assigned to (left side) and the
    expression being assigned (right side).
    """

    # Use __slots__ for memory efficiency - restricts instance attributes
    __slots__ = ("left", "right")

    def __init__(self, left: NodeVariable, right: NodeAST) -> None:
        """
        Initialize an assignment statement node.

        Args:
            left: The variable being assigned to
            right: The expression being assigned (can be any AST node)
        """
        self.left: NodeVariable = left  # Variable receiving the assignment
        self.right: NodeAST = right  # Expression being assigned

    def __repr__(self) -> str:
        """Return a string representation of the assignment statement."""
        return f"NodeAssignmentStatement(left={self.left}, right={self.right})"


class NodeCompoundStatement(NodeAST):
    """
    Represents a compound statement (block of statements) in the AST.

    This node contains a sequence of statements enclosed in BEGIN...END.
    It can contain assignment statements, other compound statements,
    or empty statements. The children list maintains statement order.
    """

    # Use __slots__ for memory efficiency - restricts instance attributes
    __slots__ = ("children",)

    def __init__(
        self,
        children: list[
            Union["NodeCompoundStatement", NodeAssignmentStatement, NodeEmpty]
        ],
    ) -> None:
        """
        Initialize a compound statement node.

        Args:
            children: List of statements contained in this compound statement
        """
        self.children: list[
            Union[NodeCompoundStatement, NodeAssignmentStatement, NodeEmpty]
        ] = children  # Statements contained in this block

    def __repr__(self) -> str:
        """Return a string representation of the compound statement."""
        return f"NodeCompoundStatement(children={self.children})"


class NodeBinaryOperation(NodeAST):
    """
    Represents a binary operation in the AST.

    This node captures operations with two operands, such as addition (a + b),
    subtraction (x - y), multiplication (p * q), etc. It stores both operands
    and the operator that connects them.
    """

    # Use __slots__ for memory efficiency - restricts instance attributes
    __slots__ = ("left", "right", "operator")

    def __init__(self, left: NodeAST, token: Token, right: NodeAST) -> None:
        """
        Initialize a binary operation node.

        Args:
            left: Left operand of the operation
            token: Token containing the operator symbol
            right: Right operand of the operation
        """
        self.left: NodeAST = left  # Left operand
        self.right: NodeAST = right  # Right operand
        self.operator: str = token.value  # Operator symbol from token

    def __repr__(self) -> str:
        """Return a string representation of the binary operation."""
        return f"NodeBinaryOperation(left={self.left}, operator={self.operator}, right={self.right})"


class NodeUnaryOperation(NodeAST):
    """
    Represents a unary operation in the AST.

    This node captures operations with a single operand, such as negation (-x)
    or positive sign (+y). It stores the operator and the operand it applies to.
    """

    # Use __slots__ for memory efficiency - restricts instance attributes
    __slots__ = ("operator", "operand")

    def __init__(self, token: Token, operand: NodeAST) -> None:
        """
        Initialize a unary operation node.

        Args:
            token: Token containing the operator symbol
            operand: The operand that the operator applies to
        """
        self.operator: str = token.value  # Operator symbol from token
        self.operand: NodeAST = operand  # Operand the operator applies to

    def __repr__(self) -> str:
        """Return a string representation of the unary operation."""
        return f"NodeUnaryOperation(operator={self.operator}, operand={self.operand})"


class NodeNumber(NodeAST):
    """
    Represents a numeric literal in the AST.

    This node stores integer and floating-point constants that appear
    in the source code. The value is extracted from the token and can
    be either an integer or float type.
    """

    # Use __slots__ for memory efficiency - restricts instance attributes
    __slots__ = ("value",)

    def __init__(self, token: Token) -> None:
        """
        Initialize a number node from a token.

        Args:
            token: Token containing the numeric value
        """
        self.value: NumericType = token.value  # Numeric value from token

    def __repr__(self) -> str:
        """Return a string representation of the number node."""
        return f"NodeNumber(value={self.value})"


class NodeBlock(NodeAST):
    """
    Represents a program block containing declarations and statements.

    A block is a fundamental structural unit that contains:
    - Variable declarations (optional)
    - Subroutine declarations (optional)
    - A compound statement with the executable code

    Blocks appear in programs, procedures, and functions.
    """

    # Use __slots__ for memory efficiency - restricts instance attributes
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
        """
        Initialize a block node.

        Args:
            variable_declarations: Variable declarations or empty if none
            subroutine_declarations: Subroutine declarations or empty if none
            compound_statement: The executable statements in this block
        """
        self.variable_declarations: Union[NodeVariableDeclarations, NodeEmpty] = (
            variable_declarations  # Variable declarations section
        )
        self.subroutine_declarations: Union[NodeSubroutineDeclarations, NodeEmpty] = (
            subroutine_declarations  # Subroutine declarations section
        )
        self.compound_statement: NodeCompoundStatement = (
            compound_statement  # Executable statements
        )

    def __repr__(self) -> str:
        """Return a string representation of the block node."""
        return "NodeBlock(variable_declarations={}, subroutine_declarations={}, compound_statement={})".format(
            self.variable_declarations,
            self.subroutine_declarations,
            self.compound_statement,
        )


class NodeParameterGroup(NodeAST):
    """
    Represents a group of parameters with the same type in a subroutine declaration.

    Similar to variable declaration groups, parameters can be declared together:
    "procedure foo(x, y: integer; z: real)" - this creates two parameter groups.
    """

    # Use __slots__ for memory efficiency - restricts instance attributes
    __slots__ = ("members", "type")

    def __init__(self, members: list[NodeVariable], type: NodeType) -> None:
        """
        Initialize a parameter group node.

        Args:
            members: List of parameters sharing the same type
            type: The type that all parameters in this group share
        """
        self.members: list[NodeVariable] = members  # Parameters in this group
        self.type: NodeType = type  # Shared type for all parameters

    def __repr__(self) -> str:
        """Return a string representation of the parameter group."""
        return f"NodeParameterGroup(members={self.members}, type={self.type})"


class NodeProcedureDeclaration(NodeAST):
    """
    Represents a procedure declaration in the AST.

    A procedure is a subroutine that performs actions but does not return
    a value. It contains a name, optional parameters, and a block of code
    to execute when called.
    """

    # Use __slots__ for memory efficiency - restricts instance attributes
    __slots__ = ("name", "parameters", "block")

    def __init__(
        self,
        name: str,
        parameters: Union[NodeEmpty, list[NodeParameterGroup]],
        block: NodeBlock,
    ) -> None:
        """
        Initialize a procedure declaration node.

        Args:
            name: Name of the procedure
            parameters: Parameter groups or empty if no parameters
            block: The code block that defines the procedure's behavior
        """
        self.name: str = name  # Procedure name
        self.parameters: Union[NodeEmpty, list[NodeParameterGroup]] = (
            parameters  # Parameter list
        )
        self.block: NodeBlock = block  # Procedure implementation

    def __repr__(self) -> str:
        """Return a string representation of the procedure declaration."""
        return "NodeProcedureDeclaration(name={}, parameters={}, block={})".format(
            self.name, self.parameters, self.block
        )


class NodeFunctionDeclaration(NodeAST):
    """
    Represents a function declaration in the AST.

    A function is a subroutine that performs calculations and returns a value.
    It contains a name, optional parameters, a return type, and a block of
    code to execute when called.
    """

    # Use __slots__ for memory efficiency - restricts instance attributes
    __slots__ = ("name", "parameters", "type", "block")

    def __init__(
        self,
        name: str,
        parameters: Union[NodeEmpty, list[NodeParameterGroup]],
        type: NodeType,
        block: NodeBlock,
    ) -> None:
        """
        Initialize a function declaration node.

        Args:
            name: Name of the function
            parameters: Parameter groups or empty if no parameters
            type: Return type of the function
            block: The code block that defines the function's behavior
        """
        self.name: str = name  # Function name
        self.parameters: Union[NodeEmpty, list[NodeParameterGroup]] = (
            parameters  # Parameter list
        )
        self.type: NodeType = type  # Return type
        self.block: NodeBlock = block  # Function implementation

    def __repr__(self) -> str:
        """Return a string representation of the function declaration."""
        return (
            "NodeFunctionDeclaration(name={}, parameters={}, type={}, block={})".format(
                self.name, self.parameters, self.type, self.block
            )
        )


class NodeSubroutineDeclarations(NodeAST):
    """
    Represents the complete subroutine declarations section of a program block.

    This node contains all procedure and function declarations that appear
    in a block. It serves as a container for organizing multiple subroutine
    declarations within a single program block.
    """

    # Use __slots__ for memory efficiency - restricts instance attributes
    __slots__ = ("declarations",)

    def __init__(
        self,
        declarations: list[Union[NodeProcedureDeclaration, NodeFunctionDeclaration]],
    ) -> None:
        """
        Initialize the subroutine declarations container.

        Args:
            declarations: List of all procedure and function declarations
        """
        self.declarations: list[
            Union[NodeProcedureDeclaration, NodeFunctionDeclaration]
        ] = declarations  # All subroutine declarations in this section

    def __repr__(self) -> str:
        """Return a string representation of the subroutine declarations."""
        return f"NodeSubroutineDeclarations(declarations={self.declarations})"


class NodeProgram(NodeAST):
    """
    Represents the root program node in the AST.

    This is the top-level node that contains the entire program structure.
    It includes the program name and the main program block containing
    all declarations and executable statements.
    """

    # Use __slots__ for memory efficiency - restricts instance attributes
    __slots__ = ("name", "block")

    def __init__(self, name: str, block: NodeBlock) -> None:
        """
        Initialize the program node.

        Args:
            name: The name of the program
            block: The main program block containing all code
        """
        self.name: str = name  # Program name
        self.block: NodeBlock = block  # Main program block

    def __repr__(self) -> str:
        """Return a string representation of the program node."""
        return f"NodeProgram(name={self.name}, block={self.block})"
