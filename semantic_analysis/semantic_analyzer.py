from visitor_pattern.visitor import NodeVisitor
from syntactic_analysis.ast import (
    NodeAST,
    NodeAssignmentStatement,
    NodeBinaryOperation,
    NodeBlock,
    NodeCompoundStatement,
    NodeFunctionDeclaration,
    NodeSubroutineDeclarations,
    NodeProcedureDeclaration,
    NodeVariableDeclarations,
    NodeEmpty,
    NodeNumber,
    NodeUnaryOperation,
    NodeVariable,
    NodeVariableDeclarationGroup,
    NodeProgram,
)
from semantic_analysis.symbol_table import (
    ScopedSymbolTable,
    VariableSymbol,
    ProgramSymbol,
    ProcedureSymbol,
    FunctionSymbol,
)
from utils.error_handling import SemanticError, ErrorCode


class SemanticAnalyzer(NodeVisitor[None]):
    """
    Semantic analyzer for Pascal-like programming language using the Visitor pattern.

    This class performs semantic analysis on an Abstract Syntax Tree (AST) to validate
    the semantic correctness of a program. It implements the second major phase of
    compilation after syntactic analysis, checking for semantic errors that cannot
    be detected by the parser alone.

    Key responsibilities:
    - Symbol table management and scope tracking
    - Variable declaration validation (no duplicates, proper scoping)
    - Variable usage validation (all variables must be declared before use)
    - Procedure and function declaration management
    - Scope creation and cleanup for nested constructs
    - Parameter list processing and validation

    The analyzer uses a scoped symbol table to track symbol visibility across
    nested scopes (global, procedure, function scopes). It follows lexical scoping
    rules where inner scopes can access symbols from outer scopes but not vice versa.

    Design Pattern:
        Visitor Pattern - Each AST node type has a corresponding visit method that
        handles the semantic analysis for that specific node type.

    Error Handling:
        Raises SemanticAnalyzerError for semantic violations like undeclared
        variables, duplicate declarations, and other semantic inconsistencies.

    Attributes:
        _current_scope: The currently active symbol table scope for symbol resolution
    """

    # Use __slots__ for memory efficiency - limits instance attributes
    __slots__ = ("_current_scope",)

    def __init__(self) -> None:
        """
        Initialize the semantic analyzer with an external (global) scope.

        The analyzer starts with a top-level "External" scope that contains
        built-in types and serves as the root of the scope hierarchy. This
        external scope is at level 0 and automatically includes built-in
        types like INTEGER and REAL.

        The scope hierarchy will be:
        External (level 0) -> Global/Program (level 1) -> Procedures/Functions (level 2+)
        """
        # Initialize with external scope containing built-in types
        # This serves as the root scope that contains language built-ins
        self._current_scope: ScopedSymbolTable = ScopedSymbolTable("External", 0, None)

    def __repr__(self) -> str:
        """Return developer-friendly string representation of the analyzer."""
        return f"{self.__class__.__name__}()"

    def __str__(self) -> str:
        """Return human-readable representation showing current scope contents."""
        return str(self._current_scope)

    def visit_NodeProgram(self, node: NodeProgram) -> None:
        """
        Analyze a program node and create the global program scope.

        This method handles the top-level program declaration by:
        1. Defining the program name as a symbol in the external scope
        2. Creating a new global scope for the program's contents
        3. Analyzing the program's block (declarations and statements)
        4. Restoring the external scope when analysis is complete

        The program scope (level 1) becomes the global scope for the entire
        program and contains all top-level declarations.

        Args:
            node: The program AST node containing program name and block

        Scope Management:
            External -> Global (created) -> External (restored)
        """
        # Define the program name in the external scope for reference
        self._current_scope.define(ProgramSymbol(node.name))

        # Create global program scope as child of external scope
        program_scope: ScopedSymbolTable = ScopedSymbolTable(
            "Global", 1, self._current_scope
        )

        # Switch to program scope for analyzing program contents
        self._current_scope = program_scope

        # Analyze the program's main block (variables, procedures, statements)
        self.visit(node.block)

        # Restore external scope - program analysis complete
        self._current_scope = self._current_scope.enclosing_scope

    def visit_NodeBlock(self, node: NodeBlock) -> None:
        """
        Analyze a block node containing declarations and statements.

        A block represents a structural unit containing variable declarations,
        subroutine declarations, and a compound statement. This method processes
        these components in the correct order:
        1. Variable declarations (must be processed first for proper scoping)
        2. Subroutine declarations (procedures and functions)
        3. Compound statement (executable statements)

        This ordering ensures that all symbols are properly defined before
        they can be referenced in executable statements.

        Args:
            node: Block AST node containing declarations and statements
        """
        # Process declarations first - variables must be declared before use
        self.visit(node.variable_declarations)

        # Process subroutine declarations - defines procedures and functions
        self.visit(node.subroutine_declarations)

        # Process executable statements - can now reference declared symbols
        self.visit(node.compound_statement)

    def visit_NodeVariableDeclarations(self, node: NodeVariableDeclarations) -> None:
        """
        Analyze variable declarations section.

        This method processes all variable declaration groups in the declarations
        section. Each group contains one or more variables of the same type.

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
        Analyze a group of variables with the same type declaration.

        This method processes a declaration like "VAR x, y, z: INTEGER;" by:
        1. Extracting the common type name
        2. Checking each variable for duplicate declarations in current scope
        3. Adding each unique variable to the current scope's symbol table

        Duplicate checking is performed only in the current scope to allow
        variable shadowing (inner scope variables hiding outer scope variables
        with the same name).

        Args:
            node: Variable declaration group with type and member variables

        Raises:
            SemanticAnalyzerError: If any variable is already declared in current scope

        Example:
            For "VAR count, total: INTEGER;" creates:
            - VariableSymbol("count", "INTEGER")
            - VariableSymbol("total", "INTEGER")
        """
        # Extract the common type name for all variables in this group
        type_name: str = node.type.name

        # Process each variable in the declaration group
        for variable in node.members:
            # Check for duplicate declaration in current scope only
            # (allows shadowing of outer scope variables)
            if (
                self._current_scope.lookup(
                    variable_name := variable.name, current_scope_only=True
                )
                is None
            ):
                # Variable not yet declared in current scope - safe to add
                self._current_scope.define(VariableSymbol(variable_name, type_name))
            else:
                # Duplicate declaration in same scope - semantic error
                raise SemanticError(
                    ErrorCode.DUPLICATE_DECLARATION,
                    f"Duplicate declaration for variable {variable_name}",
                )

    def visit_NodeCompoundStatement(self, node: NodeCompoundStatement) -> None:
        """
        Analyze a compound statement (sequence of statements).

        A compound statement is a sequence of statements enclosed in BEGIN...END.
        This method processes each child statement in order, ensuring proper
        semantic analysis of the entire statement sequence.

        Args:
            node: Compound statement AST node containing list of child statements
        """
        # Process each statement in the compound statement
        for child in node.children:
            self.visit(child)

    def visit_NodeAssignmentStatement(self, node: NodeAssignmentStatement) -> None:
        """
        Analyze an assignment statement.

        This method validates both sides of an assignment statement:
        1. Left side (variable) - must be a declared variable
        2. Right side (expression) - must be semantically valid

        The visit calls will recursively validate that all referenced variables
        are properly declared and that the expression is semantically correct.

        Args:
            node: Assignment statement AST node with left and right operands

        Note:
            Type checking (ensuring assignment compatibility) could be added
            here in a more sophisticated semantic analyzer.
        """
        # Validate left side - must be a declared variable
        self.visit(node.left)

        # Validate right side - expression must be semantically correct
        self.visit(node.right)

    def visit_NodeEmpty(self, node: NodeEmpty) -> None:
        """
        Analyze an empty node (no-op).

        Empty nodes represent optional constructs that are not present.
        No semantic analysis is needed for empty nodes.

        Args:
            node: Empty AST node (represents absence of content)
        """
        # Empty nodes require no semantic analysis
        pass

    def visit_NodeVariable(self, node: NodeVariable) -> None:
        """
        Analyze a variable reference and validate it's declared.

        This method performs variable reference validation by checking that
        the variable has been declared in the current scope or any enclosing
        scope. This implements the fundamental semantic rule that variables
        must be declared before use.

        The lookup uses scope chain traversal, allowing variables from outer
        scopes to be accessed from inner scopes (lexical scoping).

        Args:
            node: Variable AST node containing variable name

        Raises:
            SemanticAnalyzerError: If variable is not declared in any accessible scope

        Example:
            For variable reference "count", searches:
            current_scope -> parent_scope -> ... -> external_scope
        """
        # Perform scope chain lookup for the variable
        if self._current_scope.lookup(variable_name := node.name) is None:
            # Variable not found in any accessible scope
            raise SemanticError(
                ErrorCode.UNDECLARED_IDENTIFIER, f"Undeclared variable {variable_name}"
            )

    def visit_NodeNumber(self, node: NodeNumber) -> None:
        """
        Analyze a numeric literal.

        Numeric literals (integers and reals) are always semantically valid
        and require no additional analysis. The lexical analyzer has already
        validated their format, and they don't reference any symbols.

        Args:
            node: Number AST node containing numeric value
        """
        # Numeric literals are always semantically valid
        pass

    def visit_NodeBinaryOperation(self, node: NodeBinaryOperation) -> None:
        """
        Analyze a binary operation expression.

        This method validates both operands of a binary operation (like +, -, *, /).
        Both left and right operands must be semantically valid expressions.

        Args:
            node: Binary operation AST node with operator and operands

        Note:
            Type checking (ensuring operand type compatibility) could be added
            here in a more sophisticated semantic analyzer.
        """
        # Validate left operand expression
        self.visit(node.left)

        # Validate right operand expression
        self.visit(node.right)

    def visit_NodeUnaryOperation(self, node: NodeUnaryOperation) -> None:
        """
        Analyze a unary operation expression.

        This method validates the operand of a unary operation (like +x, -x).
        The operand must be a semantically valid expression.

        Args:
            node: Unary operation AST node with operator and operand

        Note:
            Type checking (ensuring operand type compatibility) could be added
            here in a more sophisticated semantic analyzer.
        """
        # Validate operand expression
        self.visit(node.operand)

    def visit_NodeSubroutineDeclarations(
        self, node: NodeSubroutineDeclarations
    ) -> None:
        """
        Analyze subroutine declarations section.

        This method processes all procedure and function declarations in the
        subroutine declarations section. Each declaration creates a new symbol
        and establishes a new scope for the subroutine's body.

        Args:
            node: Subroutine declarations AST node containing procedures and functions
        """
        # Process each subroutine declaration (procedure or function)
        for declaration in node.declarations:
            self.visit(declaration)

    def visit_NodeProcedureDeclaration(self, node: NodeProcedureDeclaration) -> None:
        """
        Analyze a procedure declaration and create procedure scope.

        This method handles procedure declarations by:
        1. Checking for duplicate procedure names in current scope
        2. Processing parameter list to create VariableSymbol objects
        3. Creating ProcedureSymbol and adding to current scope
        4. Creating new scope for procedure body
        5. Adding parameters to procedure scope
        6. Analyzing procedure body in the new scope
        7. Restoring previous scope

        Procedures create their own scope containing their parameters and local
        declarations. Parameters are treated as local variables within the
        procedure scope.

        Args:
            node: Procedure declaration AST node with name, parameters, and body

        Raises:
            SemanticAnalyzerError: If procedure name is already declared in current scope

        Scope Management:
            current_scope -> procedure_scope (created) -> current_scope (restored)

        Example:
            For "PROCEDURE DrawLine(x1, y1: INTEGER; x2, y2: REAL);"
            Creates procedure scope with parameters as local variables.
        """
        # Check for duplicate procedure declaration in current scope
        if (
            self._current_scope.lookup(
                procedure_name := node.name, current_scope_only=True
            )
            is not None
        ):
            raise SemanticError(
                ErrorCode.DUPLICATE_DECLARATION,
                f"Duplicate declaration for procedure {procedure_name}",
            )

        # Process parameter list - convert to VariableSymbol objects
        parameters: list[VariableSymbol] = []
        if not isinstance(node.parameters, NodeEmpty):
            # Parameters exist - process each parameter group
            for parameter_group in node.parameters:
                # Extend parameter list with variables from this group
                parameters.extend(
                    [
                        VariableSymbol(member.name, parameter_group.type.name)
                        for member in parameter_group.members
                    ]
                )

        # Create procedure symbol and add to current scope
        procedure_symbol: ProcedureSymbol = ProcedureSymbol(node.name, parameters)
        self._current_scope.define(procedure_symbol)

        # Create new scope for procedure body
        procedure_scope: ScopedSymbolTable = ScopedSymbolTable(
            scope_name=node.name,
            scope_level=self._current_scope.scope_level + 1,
            enclosing_scope=self._current_scope,
        )

        # Add all parameters as local variables in procedure scope
        for param in parameters:
            procedure_scope.define(param)

        # Switch to procedure scope for analyzing procedure body
        previous_scope: ScopedSymbolTable = self._current_scope
        self._current_scope = procedure_scope

        # Analyze procedure body (declarations and statements)
        self.visit(node.block)

        # Restore previous scope - procedure analysis complete
        self._current_scope = previous_scope

    def visit_NodeFunctionDeclaration(self, node: NodeFunctionDeclaration) -> None:
        """
        Analyze a function declaration and create function scope.

        This method handles function declarations by:
        1. Checking for duplicate function names in current scope
        2. Processing parameter list to create VariableSymbol objects
        3. Creating FunctionSymbol with return type and adding to current scope
        4. Creating new scope for function body
        5. Adding parameters to function scope
        6. Analyzing function body in the new scope
        7. Restoring previous scope

        Functions are similar to procedures but have a return type. They create
        their own scope containing their parameters and local declarations.
        Parameters are treated as local variables within the function scope.

        Args:
            node: Function declaration AST node with name, parameters, return type, and body

        Raises:
            SemanticAnalyzerError: If function name is already declared in current scope

        Scope Management:
            current_scope -> function_scope (created) -> current_scope (restored)

        Example:
            For "FUNCTION Max(a, b: INTEGER): INTEGER;"
            Creates function scope with parameters as local variables and INTEGER return type.
        """
        # Check for duplicate function declaration in current scope
        if (
            self._current_scope.lookup(
                function_name := node.name, current_scope_only=True
            )
            is not None
        ):
            raise SemanticError(
                ErrorCode.DUPLICATE_DECLARATION,
                f"Duplicate declaration for function {function_name}",
            )

        # Process parameter list - convert to VariableSymbol objects
        parameters: list[VariableSymbol] = []
        if not isinstance(node.parameters, NodeEmpty):
            # Parameters exist - process each parameter group
            for parameter_group in node.parameters:
                # Extend parameter list with variables from this group
                parameters.extend(
                    [
                        VariableSymbol(variable.name, parameter_group.type.name)
                        for variable in parameter_group.members
                    ]
                )

        # Create function symbol with return type and add to current scope
        function_symbol: FunctionSymbol = FunctionSymbol(
            node.name, parameters, node.type.name
        )
        self._current_scope.define(function_symbol)

        # Create new scope for function body
        function_scope: ScopedSymbolTable = ScopedSymbolTable(
            scope_name=node.name,
            scope_level=self._current_scope.scope_level + 1,
            enclosing_scope=self._current_scope,
        )

        # Add all parameters as local variables in function scope
        for param in parameters:
            function_scope.define(param)

        # Switch to function scope for analyzing function body
        previous_scope: ScopedSymbolTable = self._current_scope
        self._current_scope = function_scope

        # Analyze function body (declarations and statements)
        self.visit(node.block)

        # Restore previous scope - function analysis complete
        self._current_scope = previous_scope

    def analyze(self, tree: NodeAST) -> None:
        """
        Perform complete semantic analysis on an AST.

        This is the main public interface for the semantic analyzer. It starts
        the semantic analysis process by visiting the root node of the AST,
        which triggers the recursive analysis of the entire program structure.

        The analysis validates:
        - All variables are declared before use
        - No duplicate declarations in the same scope
        - Proper scope management for nested constructs
        - Correct subroutine declaration and usage patterns

        Args:
            tree: Root AST node (typically a NodeProgram) to analyze

        Raises:
            SemanticAnalyzerError: For any semantic violations found during analysis

        Usage:
            analyzer = SemanticAnalyzer()
            analyzer.analyze(ast_root)  # Performs complete semantic analysis
        """
        # Start semantic analysis from the root node
        # This will recursively analyze the entire program structure
        self.visit(tree)
