from typing import Callable, Optional, Union
import operator
from visitor_pattern.visitor import NodeVisitor
from syntactic_analysis.ast import (
    NodeAST,
    NodeBinaryOperation,
    NodeBlock,
    NodeFunctionDeclaration,
    NodeSubroutineDeclarations,
    NodeProcedureDeclaration,
    NodeVariableDeclarations,
    NodeEmpty,
    NodeAssignmentStatement,
    NodeProgram,
    NodeVariable,
    NodeCompoundStatement,
    NodeNumber,
    NodeUnaryOperation,
    NodeVariableDeclarationGroup,
)
from utils.error_handling import InterpreterError, ErrorCode

# Type aliases for better code documentation and type safety
# ValueType represents all possible values that can be stored in interpreter memory
ValueType = Union[int, float, str]

# NumericType represents values that can participate in arithmetic operations
NumericType = Union[int, float]


class Interpreter(NodeVisitor[Optional[ValueType]]):
    """
    Tree-walking interpreter for Pascal-like programming language.

    This interpreter executes programs by traversing the Abstract Syntax Tree (AST)
    and performing the operations represented by each node. It implements the final
    phase of a simple compiler/interpreter pipeline, taking a semantically validated
    AST and producing program output through execution.

    The interpreter uses the Visitor pattern to dispatch execution to appropriate
    methods based on AST node types. It maintains a simple global memory model
    for variable storage and supports basic arithmetic operations, variable
    assignments, and control flow.

    Key Features:
    - Direct AST execution (tree-walking interpretation)
    - Global memory model for variable storage
    - Arithmetic expression evaluation with operator precedence
    - Type-aware default value initialization
    - Division by zero error detection
    - Support for integer and floating-point arithmetic

    Architecture:
    - Uses visitor pattern for AST traversal and execution
    - Maintains global memory dictionary for variable storage
    - Operator dispatch through function dictionaries
    - Type-safe value handling with Union types

    Current Limitations:
    - Only supports global scope (no nested scopes or procedures/functions)
    - Limited to basic arithmetic and assignment operations
    - No control flow statements (if, while, for)
    - No procedure/function call mechanisms

    Memory Model:
        Global memory is implemented as a simple dictionary mapping variable
        names to their current values. All variables exist in global scope
        and are initialized with type-appropriate default values.

    Attributes:
        _global_memory: Dictionary storing variable names and their runtime values
    """

    # Use __slots__ for memory efficiency - restricts instance attributes
    __slots__ = ("_global_memory",)

    # Class-level operator dispatch tables for efficient operation lookup
    # These dictionaries map operator symbols to their corresponding Python functions
    # Using operator module functions provides optimized implementations

    BINARY_OPERATORS: dict[str, Callable[[NumericType, NumericType], NumericType]] = {
        "+": operator.add,  # Addition: a + b
        "-": operator.sub,  # Subtraction: a - b
        "*": operator.mul,  # Multiplication: a * b
        "/": operator.truediv,  # Real division: a / b (always returns float)
        "DIV": operator.floordiv,  # Integer division: a DIV b (returns integer)
        "MOD": operator.mod,  # Modulo: a MOD b (remainder after division)
    }

    UNARY_OPERATORS: dict[str, Callable[[NumericType], NumericType]] = {
        "+": operator.pos,  # Unary plus: +a (identity operation)
        "-": operator.neg,  # Unary minus: -a (negation)
    }

    # Default values for each supported data type
    # Variables are initialized to these values when declared
    TYPES_DEFAULT_VALUES: dict[str, ValueType] = {
        "INTEGER": 0,  # Integer variables default to zero
        "REAL": 0.0,  # Real variables default to zero point zero
    }

    def __init__(self) -> None:
        """
        Initialize the interpreter with empty global memory.

        The interpreter starts with no variables defined. Variables will be
        added to global memory as they are encountered during variable
        declaration processing.
        """
        # Initialize empty global memory for storing variable values
        # Key: variable name (string), Value: current variable value
        self._global_memory: dict[str, ValueType] = {}

    def __repr__(self) -> str:
        """Return developer-friendly string representation of the interpreter."""
        return f"Interpreter()"

    def __str__(self) -> str:
        """Return human-readable representation showing current memory state."""
        return str(self._global_memory)

    def visit_NodeProgram(self, node: NodeProgram) -> None:
        """
        Execute a program by running its main block.

        The program node represents the top-level program structure. Execution
        begins here and proceeds by executing the program's main block, which
        contains all variable declarations, subroutine declarations, and the
        main executable statements.

        Args:
            node: Program AST node containing the program name and main block

        Note:
            The program name is not used during execution - it's primarily
            for identification and linking purposes in more complex systems.
        """
        # Execute the program's main block (declarations + statements)
        self.visit(node.block)

    def visit_NodeBlock(self, node: NodeBlock) -> None:
        """
        Execute a block by processing declarations and statements in order.

        A block contains three main components that must be executed in sequence:
        1. Variable declarations - allocate and initialize variables
        2. Subroutine declarations - process procedure/function definitions
        3. Compound statement - execute the main program logic

        This ordering ensures that all variables and subroutines are properly
        defined before any executable statements attempt to use them.

        Args:
            node: Block AST node containing declarations and executable statements
        """
        # Process variable declarations first - allocate memory for variables
        self.visit(node.variable_declarations)

        # Process subroutine declarations - currently no-op in this interpreter
        self.visit(node.subroutine_declarations)

        # Execute the main program logic
        self.visit(node.compound_statement)

    def visit_NodeVariableDeclarations(self, node: NodeVariableDeclarations) -> None:
        """
        Process all variable declaration groups in the declarations section.

        This method iterates through all variable declaration groups and
        processes each one to allocate memory and initialize variables
        with their default values.

        Args:
            node: Variable declarations AST node containing list of declaration groups
        """
        # Process each variable declaration group
        for declaration in node.variable_declarations:
            self.visit(declaration)

    def visit_NodeVariableDeclarationGroup(
        self, node: NodeVariableDeclarationGroup
    ) -> None:
        """
        Process a group of variables with the same type declaration.

        This method handles variable declarations like "VAR x, y, z: INTEGER;"
        by allocating memory for each variable and initializing them with
        the appropriate default value based on their declared type.

        The interpreter uses a simple global memory model where all variables
        are stored in a single dictionary with their names as keys.

        Args:
            node: Variable declaration group with type and member variables

        Example:
            For "VAR count, total: INTEGER;" this method:
            1. Gets default value 0 for INTEGER type
            2. Adds count -> 0 to global memory
            3. Adds total -> 0 to global memory
        """
        # Get the default value for this type (e.g., 0 for INTEGER, 0.0 for REAL)
        default_value: ValueType = self.TYPES_DEFAULT_VALUES[node.type.name]

        # Initialize each variable in the group with the default value
        for variable in node.members:
            self._global_memory[variable.name] = default_value

    def visit_NodeSubroutineDeclarations(
        self, node: NodeSubroutineDeclarations
    ) -> None:
        """
        Process subroutine declarations (procedures and functions).

        This method iterates through all subroutine declarations in the
        declarations section. In the current interpreter implementation,
        subroutines are not fully supported, so the individual visit
        methods for procedures and functions are no-ops.

        Args:
            node: Subroutine declarations AST node containing procedures and functions

        Note:
            This provides the framework for future subroutine support
            when the interpreter is extended with call stack management
            and local scope handling.
        """
        # Process each subroutine declaration (currently no-op)
        for declaration in node.declarations:
            self.visit(declaration)

    def visit_NodeProcedureDeclaration(self, node: NodeProcedureDeclaration) -> None:
        """
        Process a procedure declaration (currently not implemented).

        Procedures are subroutines that perform actions but don't return values.
        The current interpreter does not support procedure calls or local scopes,
        so procedure declarations are ignored during execution.

        Args:
            node: Procedure declaration AST node

        Future Enhancement:
            Full procedure support would require:
            - Call stack management for nested calls
            - Local scope creation and cleanup
            - Parameter passing mechanisms
            - Control flow for procedure entry/exit
        """
        # Procedure execution not implemented in this simple interpreter
        pass

    def visit_NodeFunctionDeclaration(self, node: NodeFunctionDeclaration) -> None:
        """
        Process a function declaration (currently not implemented).

        Functions are subroutines that return values of specific types.
        The current interpreter does not support function calls or local scopes,
        so function declarations are ignored during execution.

        Args:
            node: Function declaration AST node

        Future Enhancement:
            Full function support would require:
            - Call stack management for nested calls
            - Local scope creation and cleanup
            - Parameter passing mechanisms
            - Return value handling
            - Control flow for function entry/exit
        """
        # Function execution not implemented in this simple interpreter
        pass

    def visit_NodeEmpty(self, node: NodeEmpty) -> None:
        """
        Process an empty node (no operation required).

        Empty nodes represent optional language constructs that are not present
        in the current program. No execution is required for empty nodes.

        Args:
            node: Empty AST node representing absence of content
        """
        # Empty nodes require no execution
        pass

    def visit_NodeAssignmentStatement(self, node: NodeAssignmentStatement) -> None:
        """
        Execute an assignment statement by evaluating RHS and storing in LHS variable.

        Assignment statements have the form "variable := expression" and are
        executed by:
        1. Evaluating the right-hand side expression to get a value
        2. Storing that value in the left-hand side variable's memory location

        This implementation assumes the left-hand side is always a simple variable
        (not an array element or record field).

        Args:
            node: Assignment statement AST node with left and right operands

        Note:
            The semantic analyzer should have already validated that:
            - The left-hand side variable is declared
            - The right-hand side expression is semantically valid
        """
        # Get the target variable name from the left-hand side
        variable_name: str = node.left.name

        # Evaluate the right-hand side expression to get the value
        result: Optional[ValueType] = self.visit(node.right)

        # Store the result in the variable's memory location
        if result is not None:
            self._global_memory[variable_name] = result

    def visit_NodeVariable(self, node: NodeVariable) -> ValueType:
        """
        Retrieve the current value of a variable from memory.

        This method implements variable reference by looking up the variable's
        current value in global memory. The semantic analyzer should have
        already validated that the variable is declared.

        Args:
            node: Variable AST node containing the variable name

        Returns:
            The current value stored in the variable

        Note:
            In a more robust interpreter, this would include error checking
            for undefined variables, but we rely on semantic analysis to
            catch such errors before execution.
        """
        # Get variable name and look up its current value
        variable_name: str = node.name
        return self._global_memory[variable_name]

    def visit_NodeCompoundStatement(self, node: NodeCompoundStatement) -> None:
        """
        Execute a compound statement by executing all child statements in sequence.

        A compound statement (BEGIN...END block) contains a sequence of statements
        that are executed in order. This method processes each child statement
        sequentially, maintaining the proper execution flow.

        Args:
            node: Compound statement AST node containing list of child statements
        """
        # Execute each child statement in sequence
        for child in node.children:
            self.visit(child)

    def visit_NodeBinaryOperation(self, node: NodeBinaryOperation) -> NumericType:
        """
        Evaluate a binary arithmetic operation.

        Binary operations have the form "left_operand operator right_operand"
        and are evaluated by:
        1. Evaluating both operands to get numeric values
        2. Looking up the operator function in the dispatch table
        3. Applying the operator function to the operand values
        4. Returning the computed result

        Special handling is provided for division operations to detect and
        prevent division by zero errors.

        Args:
            node: Binary operation AST node with operator and operands

        Returns:
            The computed result of applying the operator to the operands

        Raises:
            InterpreterError: If division by zero is attempted

        Supported Operators:
            +     Addition (works with int + int -> int, float + float -> float, mixed -> float)
            -     Subtraction (same type rules as addition)
            *     Multiplication (same type rules as addition)
            /     Real division (always returns float)
            DIV   Integer division (returns int, truncates toward zero)
            MOD   Modulo (returns remainder after integer division)
        """
        # Evaluate both operands to get their numeric values
        left_val: NumericType = self.visit(node.left)
        right_val: NumericType = self.visit(node.right)

        # Normalize operator symbol to uppercase for consistent lookup
        operator_symbol: str = node.operator.upper()

        # Check for division by zero before performing division operations
        if operator_symbol in ("/", "DIV", "MOD") and right_val in (0, 0.0):
            raise InterpreterError(ErrorCode.DIVISION_BY_ZERO, "Cannot divide by zero")

        # Look up and apply the operator function
        return self.BINARY_OPERATORS[operator_symbol](left_val, right_val)

    def visit_NodeUnaryOperation(self, node: NodeUnaryOperation) -> NumericType:
        """
        Evaluate a unary arithmetic operation.

        Unary operations have the form "operator operand" and are evaluated by:
        1. Evaluating the operand to get a numeric value
        2. Looking up the operator function in the dispatch table
        3. Applying the operator function to the operand value
        4. Returning the computed result

        Args:
            node: Unary operation AST node with operator and operand

        Returns:
            The computed result of applying the operator to the operand

        Supported Operators:
            +   Unary plus (identity operation - returns operand unchanged)
            -   Unary minus (negation - returns negative of operand)
        """
        # Evaluate the operand to get its numeric value
        operand_val: NumericType = self.visit(node.operand)

        # Normalize operator symbol to uppercase for consistent lookup
        operator_symbol: str = node.operator.upper()

        # Look up and apply the operator function
        return self.UNARY_OPERATORS[operator_symbol](operand_val)

    def visit_NodeNumber(self, node: NodeNumber) -> NumericType:
        """
        Return the numeric value of a number literal.

        Number literals represent constant values in the program (like 42 or 3.14).
        This method simply returns the parsed numeric value stored in the AST node.

        Args:
            node: Number AST node containing the parsed numeric value

        Returns:
            The numeric value (int for integer literals, float for real literals)

        Note:
            The lexical analyzer has already performed number parsing and validation,
            so we can safely return the stored value without additional processing.
        """
        # Return the pre-parsed numeric value
        return node.value

    def interpret(self, tree: NodeAST) -> Optional[ValueType]:
        """
        Execute a complete program represented by an AST.

        This is the main public interface for the interpreter. It starts execution
        at the root of the AST (typically a NodeProgram) and returns any value
        produced by the program execution.

        The interpretation process:
        1. Starts at the root AST node
        2. Recursively visits and executes all nodes in the tree
        3. Maintains global memory state throughout execution
        4. Returns final result (typically None for programs)

        Args:
            tree: Root AST node (typically NodeProgram) representing the program

        Returns:
            Optional value produced by program execution (usually None for programs)

        Raises:
            InterpreterError: For runtime errors like division by zero
            KeyError: If undeclared variables are accessed (should be caught by semantic analysis)

        Usage:
            interpreter = Interpreter()
            result = interpreter.interpret(ast_root)  # Execute the program
            print(interpreter)  # Show final memory state
        """
        # Start interpretation from the root node
        # This will recursively execute the entire program
        return self.visit(tree)
