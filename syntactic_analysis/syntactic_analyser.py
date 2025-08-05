from typing import Union
from lexical_analysis.lexical_analyzer import LexicalAnalyzer
from lexical_analysis.tokens import Token, TokenType
from syntactic_analysis.ast import (
    NodeAST,
    NodeBlock,
    NodeFunctionDeclaration,
    NodeParameterGroup,
    NodeSubroutineDeclarations,
    NodeProcedureDeclaration,
    NodeVariableDeclarations,
    NodeEmpty,
    NodeProgram,
    NodeType,
    NodeVariable,
    NodeAssignmentStatement,
    NodeCompoundStatement,
    NodeBinaryOperation,
    NodeNumber,
    NodeUnaryOperation,
    NodeVariableDeclarationGroup,
)
from utils.error_handling import SyntacticError, ErrorCode


class SyntacticAnalyzer(object):
    """
    A syntactic analyzer (parser) that constructs an Abstract Syntax Tree (AST) from tokens.

    This parser implements a recursive descent parser for a Pascal-like programming language.
    It consumes tokens produced by the lexical analyzer and builds a hierarchical AST
    representation of the program structure. The parser enforces the language's grammar
    rules and provides meaningful error messages for syntax violations.

    Grammar (in Backus-Naur Form):
    program ::= PROGRAM variable SEMICOLON block DOT
    block ::= variable_declarations subroutine_declarations compound_statement
    variable_declarations ::= VAR (variable_declaration SEMICOLON)+ | empty
    variable_declaration ::= variable (COMMA variable)* COLON type
    subroutine_declarations ::= ((procedure_declaration | function_declaration) SEMICOLON)*
    procedure_declaration ::= PROCEDURE variable (LEFT_PARENTHESIS parameters RIGHT_PARENTHESIS)? SEMICOLON block
    function_declaration ::= FUNCTION variable (LEFT_PARENTHESIS parameters RIGHT_PARENTHESIS)? COLON type SEMICOLON block
    parameters ::= parameter_group (SEMICOLON parameter_group)*
    parameter_group ::= variable (COMMA variable)* COLON type
    type ::= INTEGER | REAL
    compound_statement ::= BEGIN statement_list END
    statement_list ::= statement | statement SEMICOLON statement_list
    statement ::= compound_statement | assignment_statement | empty
    assignment_statement ::= variable ASSIGN expression
    expression ::= term ((PLUS | MINUS) term)*
    term ::= factor ((MUL | TRUE_DIV | INTEGER_DIV | MOD) factor)*
    factor ::= (PLUS | MINUS)? (INTEGER | REAL | LEFT_PARENTHESIS expression RIGHT_PARENTHESIS | variable)
    variable ::= ID
    empty ::=
    """

    # Use __slots__ for memory efficiency - restricts instance attributes to these only
    __slots__ = ("_lexical_analyzer", "_current_token")

    def __init__(self, lexer: LexicalAnalyzer) -> None:
        """
        Initialize the syntactic analyzer with a lexical analyzer.

        Args:
            lexer: The lexical analyzer that provides tokens for parsing
        """
        self._lexical_analyzer: LexicalAnalyzer = lexer  # Token source for parsing
        self._current_token: Token = (
            self._lexical_analyzer.next_token()
        )  # Current token being processed

    def _consume(self, expected_type: TokenType) -> Token:
        """
        Consume the current token if it matches the expected type.

        This method verifies that the current token is of the expected type,
        advances to the next token if successful, or raises an error if not.
        It's the core mechanism for enforcing grammar rules.

        Args:
            expected_type: The token type that should be current

        Returns:
            The consumed token

        Raises:
            SyntacticAnalyzerError: If current token doesn't match expected type
        """
        if self._current_token.type == expected_type:
            token: Token = self._current_token  # Save current token to return
            self._current_token = (
                self._lexical_analyzer.next_token()
            )  # Advance to next token
            return token
        else:
            raise SyntacticError(
                ErrorCode.UNEXPECTED_TOKEN,
                f"Expected {expected_type.value}",
                self._current_token,
            )

    def _program(self) -> NodeProgram:
        """
        Parse a complete program structure.

        Grammar: program ::= PROGRAM variable SEMICOLON block DOT

        This method parses the top-level program construct, which consists of
        the PROGRAM keyword, program name, declarations, and executable code.

        Returns:
            NodeProgram representing the complete program structure
        """
        self._consume(TokenType.PROGRAM)  # Consume PROGRAM keyword
        program_name: str = self._variable().name  # Get program name
        self._consume(TokenType.SEMICOLON)  # Consume semicolon after name
        block: NodeBlock = self._block()  # Parse program body
        self._consume(TokenType.DOT)  # Consume final dot
        return NodeProgram(program_name, block)

    def _block(self) -> NodeBlock:
        """
        Parse a program block containing declarations and statements.

        Grammar: block ::= variable_declarations subroutine_declarations compound_statement

        A block represents a scope containing variable declarations, subroutine
        declarations, and executable statements. Blocks appear in programs,
        procedures, and functions.

        Returns:
            NodeBlock containing all declarations and statements in this scope
        """
        variable_declarations: Union[NodeVariableDeclarations, NodeEmpty] = (
            self._variable_declarations()  # Parse variable declarations section
        )
        subroutine_declarations: NodeSubroutineDeclarations = (
            self._subroutine_declarations()  # Parse procedure/function declarations
        )
        compound_statement: NodeCompoundStatement = (
            self._compound_statement()
        )  # Parse executable statements
        return NodeBlock(
            variable_declarations,
            subroutine_declarations,
            compound_statement,
        )

    def _subroutine_declarations(
        self,
    ) -> NodeSubroutineDeclarations:
        """
        Parse subroutine declarations (procedures and functions).

        Grammar: subroutine_declarations ::= ((procedure_declaration | function_declaration) SEMICOLON)*

        This method handles zero or more procedure and function declarations
        that appear before the main compound statement in a block.

        Returns:
            NodeSubroutineDeclarations containing all parsed subroutines
        """
        subroutine_declarations: list[
            Union[NodeProcedureDeclaration, NodeFunctionDeclaration]
        ] = []

        # Parse procedure and function declarations until none remain
        while self._current_token.type in (TokenType.PROCEDURE, TokenType.FUNCTION):
            if self._current_token.type == TokenType.PROCEDURE:
                subroutine_declarations.append(
                    self._procedure_declaration()
                )  # Parse procedure
            else:
                subroutine_declarations.append(
                    self._function_declaration()
                )  # Parse function
            self._consume(TokenType.SEMICOLON)  # Consume semicolon after declaration
        return NodeSubroutineDeclarations(subroutine_declarations)

    def _procedure_declaration(self) -> NodeProcedureDeclaration:
        """
        Parse a procedure declaration.

        Grammar: procedure_declaration ::= PROCEDURE variable (LEFT_PARENTHESIS parameters RIGHT_PARENTHESIS)? SEMICOLON block

        Procedures are subroutines that perform actions but don't return values.
        They can have optional parameters and contain their own block of code.

        Returns:
            NodeProcedureDeclaration representing the procedure definition
        """
        self._consume(TokenType.PROCEDURE)  # Consume PROCEDURE keyword
        procedure_name: str = self._variable().name  # Get procedure name
        parameters: Union[NodeEmpty, list[NodeParameterGroup]] = (
            NodeEmpty()
        )  # Default to no parameters

        # Parse optional parameter list
        if self._current_token.type == TokenType.LEFT_PARENTHESIS:
            self._consume(TokenType.LEFT_PARENTHESIS)  # Consume opening parenthesis
            parameters = self._parameters()  # Parse parameter list
            self._consume(TokenType.RIGHT_PARENTHESIS)  # Consume closing parenthesis

        self._consume(TokenType.SEMICOLON)  # Consume semicolon before block
        block: NodeBlock = self._block()  # Parse procedure body
        return NodeProcedureDeclaration(procedure_name, parameters, block)

    def _function_declaration(self) -> NodeFunctionDeclaration:
        """
        Parse a function declaration.

        Grammar: function_declaration ::= FUNCTION variable (LEFT_PARENTHESIS parameters RIGHT_PARENTHESIS)? COLON type SEMICOLON block

        Functions are subroutines that perform calculations and return values.
        They can have optional parameters and must specify a return type.

        Returns:
            NodeFunctionDeclaration representing the function definition
        """
        self._consume(TokenType.FUNCTION)  # Consume FUNCTION keyword
        function_name: str = self._variable().name  # Get function name
        parameters: Union[NodeEmpty, list[NodeParameterGroup]] = (
            NodeEmpty()
        )  # Default to no parameters

        # Parse optional parameter list
        if self._current_token.type == TokenType.LEFT_PARENTHESIS:
            self._consume(TokenType.LEFT_PARENTHESIS)  # Consume opening parenthesis
            parameters = self._parameters()  # Parse parameter list
            self._consume(TokenType.RIGHT_PARENTHESIS)  # Consume closing parenthesis

        self._consume(TokenType.COLON)  # Consume colon before return type
        return_type: NodeType = self._type()  # Parse return type
        self._consume(TokenType.SEMICOLON)  # Consume semicolon before block
        block: NodeBlock = self._block()  # Parse function body
        return NodeFunctionDeclaration(function_name, parameters, return_type, block)

    def _parameters(self) -> list[NodeParameterGroup]:
        """
        Parse a parameter list for procedures and functions.

        Grammar: parameters ::= parameter_group (SEMICOLON parameter_group)*

        Parameters are organized into groups where each group contains variables
        of the same type, separated by semicolons.

        Returns:
            List of NodeParameterGroup objects representing all parameter groups
        """
        parameters: list[NodeParameterGroup] = [
            self._parameter_group()
        ]  # Parse first parameter group

        # Parse additional parameter groups separated by semicolons
        while self._current_token.type == TokenType.SEMICOLON:
            self._consume(TokenType.SEMICOLON)  # Consume semicolon separator
            parameters.append(self._parameter_group())  # Parse next parameter group
        return parameters

    def _parameter_group(self) -> NodeParameterGroup:
        """
        Parse a group of parameters with the same type.

        Grammar: parameter_group ::= variable (COMMA variable)* COLON type

        A parameter group consists of one or more variable names followed
        by their shared type specification.

        Returns:
            NodeParameterGroup containing variables and their shared type
        """
        variables: list[NodeVariable] = [self._variable()]  # Parse first variable

        # Parse additional variables separated by commas
        while self._current_token.type == TokenType.COMMA:
            self._consume(TokenType.COMMA)  # Consume comma separator
            variables.append(self._variable())  # Parse next variable

        self._consume(TokenType.COLON)  # Consume colon before type
        type: NodeType = self._type()  # Parse shared type
        return NodeParameterGroup(variables, type)

    def _variable_declarations(self) -> Union[NodeVariableDeclarations, NodeEmpty]:
        """
        Parse variable declarations section.

        Grammar: variable_declarations ::= VAR (variable_declaration SEMICOLON)+ | empty

        The variable declarations section is optional and starts with the VAR
        keyword followed by one or more variable declaration groups.

        Returns:
            NodeVariableDeclarations if declarations exist, NodeEmpty otherwise
        """
        if self._current_token.type == TokenType.VAR:
            self._consume(TokenType.VAR)  # Consume VAR keyword
            variable_declarations: list[NodeVariableDeclarationGroup] = []

            # Parse variable declaration groups until none remain
            while self._current_token.type == TokenType.ID:
                variable_declarations.append(
                    self._variable_declaration()
                )  # Parse declaration group
                self._consume(TokenType.SEMICOLON)  # Consume semicolon after group
            return NodeVariableDeclarations(variable_declarations)
        else:
            return self._empty()  # No variable declarations present

    def _variable_declaration(self) -> NodeVariableDeclarationGroup:
        """
        Parse a group of variable declarations with the same type.

        Grammar: variable_declaration ::= variable (COMMA variable)* COLON type

        Variable declarations group multiple variables of the same type together,
        such as "x, y, z: integer".

        Returns:
            NodeVariableDeclarationGroup containing variables and their shared type
        """
        variables: list[NodeVariable] = [self._variable()]  # Parse first variable

        # Parse additional variables separated by commas
        while self._current_token.type == TokenType.COMMA:
            self._consume(TokenType.COMMA)  # Consume comma separator
            variables.append(self._variable())  # Parse next variable

        self._consume(TokenType.COLON)  # Consume colon before type
        node_type: NodeType = self._type()  # Parse shared type
        return NodeVariableDeclarationGroup(variables, node_type)

    def _type(self) -> NodeType:
        """
        Parse a type specification.

        Grammar: type ::= INTEGER | REAL

        Types specify the data type for variables, parameters, and function
        return values. Currently supports INTEGER and REAL types.

        Returns:
            NodeType representing the parsed type

        Raises:
            SyntacticAnalyzerError: If neither INTEGER nor REAL is found
        """
        token: Token = self._current_token
        if token.type == TokenType.INTEGER:
            self._consume(TokenType.INTEGER)  # Consume INTEGER keyword
            return NodeType(token)
        elif token.type == TokenType.REAL:
            self._consume(TokenType.REAL)  # Consume REAL keyword
            return NodeType(token)
        else:
            raise SyntacticError(
                ErrorCode.UNEXPECTED_TOKEN, "Expected INTEGER or REAL", token
            )

    def _statement(
        self,
    ) -> Union[NodeCompoundStatement, NodeAssignmentStatement, NodeEmpty]:
        """
        Parse a single statement.

        Grammar: statement ::= compound_statement | assignment_statement | empty

        Statements are the executable units of the program. They can be
        compound statements (blocks), assignment statements, or empty statements.

        Returns:
            AST node representing the parsed statement
        """
        if self._current_token.type == TokenType.BEGIN:
            return self._compound_statement()  # Parse compound statement
        elif self._current_token.type == TokenType.ID:
            return self._assignment_statement()  # Parse assignment statement
        else:
            return self._empty()  # Parse empty statement

    def _compound_statement(self) -> NodeCompoundStatement:
        """
        Parse a compound statement (statement block).

        Grammar: compound_statement ::= BEGIN statement_list END

        Compound statements group multiple statements together within
        BEGIN...END delimiters, creating a single logical statement unit.

        Returns:
            NodeCompoundStatement containing all statements in the block
        """
        self._consume(TokenType.BEGIN)  # Consume BEGIN keyword
        children: list[
            Union[NodeCompoundStatement, NodeAssignmentStatement, NodeEmpty]
        ] = self._statement_list()  # Parse all statements in the block
        self._consume(TokenType.END)  # Consume END keyword
        return NodeCompoundStatement(children)

    def _assignment_statement(self) -> NodeAssignmentStatement:
        """
        Parse an assignment statement.

        Grammar: assignment_statement ::= variable ASSIGN expression

        Assignment statements assign the result of an expression to a variable
        using the := operator.

        Returns:
            NodeAssignmentStatement representing the assignment operation
        """
        _variable: NodeVariable = self._variable()  # Parse target variable
        self._consume(TokenType.ASSIGN)  # Consume := operator
        return NodeAssignmentStatement(
            _variable, self._expression()
        )  # Parse assigned expression

    def _empty(self) -> NodeEmpty:
        """
        Parse an empty statement.

        Grammar: empty ::=

        Empty statements represent the absence of an actual statement.
        They're used as placeholders in optional statement positions.

        Returns:
            NodeEmpty representing the absence of a statement
        """
        return NodeEmpty()

    def _statement_list(
        self,
    ) -> list[Union[NodeCompoundStatement, NodeAssignmentStatement, NodeEmpty]]:
        """
        Parse a list of statements separated by semicolons.

        Grammar: statement_list ::= statement | statement SEMICOLON statement_list

        Statement lists contain one or more statements separated by semicolons.
        They appear within compound statements and define execution order.

        Returns:
            List of AST nodes representing all statements in the list
        """
        nodes: list[
            Union[NodeCompoundStatement, NodeAssignmentStatement, NodeEmpty]
        ] = [
            self._statement()
        ]  # Parse first statement

        # Parse additional statements separated by semicolons
        while self._current_token.type == TokenType.SEMICOLON:
            self._consume(TokenType.SEMICOLON)  # Consume semicolon separator
            nodes.append(self._statement())  # Parse next statement
        return nodes

    def _variable(self) -> NodeVariable:
        """
        Parse a variable identifier.

        Grammar: variable ::= ID

        Variables are identifiers that represent memory locations for storing
        values. They can be used in expressions and as assignment targets.

        Returns:
            NodeVariable representing the variable identifier
        """
        token: Token = self._current_token  # Save current token
        self._consume(TokenType.ID)  # Consume identifier token
        return NodeVariable(token)

    def _factor(self) -> NodeAST:
        """
        Parse a factor in an expression.

        Grammar: factor ::= (PLUS | MINUS)? (INTEGER | REAL | LEFT_PARENTHESIS expression RIGHT_PARENTHESIS | variable)

        Factors are the basic building blocks of expressions. They can be
        numbers, variables, parenthesized expressions, or unary operations.

        Returns:
            AST node representing the parsed factor

        Raises:
            SyntacticAnalyzerError: If no valid factor is found
        """
        token: Token = self._current_token
        if token.type == TokenType.ID:
            return self._variable()  # Parse variable
        elif token.type == TokenType.INTEGER_CONSTANT:
            self._consume(TokenType.INTEGER_CONSTANT)  # Consume integer literal
            return NodeNumber(token)
        elif token.type == TokenType.REAL_CONSTANT:
            self._consume(TokenType.REAL_CONSTANT)  # Consume real literal
            return NodeNumber(token)
        elif token.type == TokenType.LEFT_PARENTHESIS:
            self._consume(TokenType.LEFT_PARENTHESIS)  # Consume opening parenthesis
            node: NodeAST = self._expression()  # Parse parenthesized expression
            self._consume(TokenType.RIGHT_PARENTHESIS)  # Consume closing parenthesis
            return node
        elif token.type in (TokenType.PLUS, TokenType.MINUS):
            self._consume(token.type)  # Consume unary operator
            operand: NodeAST = self._factor()  # Parse operand
            return NodeUnaryOperation(token, operand)
        else:
            raise SyntacticError(
                ErrorCode.UNEXPECTED_TOKEN,
                "Expected number, unary operator, or '('",
                token,
            )

    def _term(self) -> NodeAST:
        """
        Parse a term in an expression.

        Grammar: term ::= factor ((MUL | TRUE_DIV | INTEGER_DIV | MOD) factor)*

        Terms handle multiplication, division, and modulo operations.
        They have higher precedence than addition and subtraction.

        Returns:
            AST node representing the parsed term with all its operations
        """
        node: NodeAST = self._factor()  # Parse first factor

        # Parse multiplication, division, and modulo operations
        while self._current_token.type in (
            TokenType.MUL,
            TokenType.DIV,
            TokenType.TRUE_DIV,
            TokenType.MOD,
        ):
            token: Token = self._current_token  # Save operator token
            self._consume(token.type)  # Consume operator
            right: NodeAST = self._factor()  # Parse right operand
            node = NodeBinaryOperation(node, token, right)  # Build binary operation
        return node

    def _expression(self) -> NodeAST:
        """
        Parse an expression.

        Grammar: expression ::= term ((PLUS | MINUS) term)*

        Expressions handle addition and subtraction operations.
        They have lower precedence than multiplication and division.

        Returns:
            AST node representing the parsed expression with all its operations
        """
        node: NodeAST = self._term()  # Parse first term

        # Parse addition and subtraction operations
        while self._current_token.type in (TokenType.PLUS, TokenType.MINUS):
            token: Token = self._current_token  # Save operator token
            self._consume(token.type)  # Consume operator
            right: NodeAST = self._term()  # Parse right operand
            node = NodeBinaryOperation(node, token, right)  # Build binary operation
        return node

    def parse(self) -> NodeAST:
        """
        Parse the complete input and return the AST root.

        This is the main entry point for parsing. It parses a complete program
        and ensures that all input tokens have been consumed successfully.

        Returns:
            NodeAST representing the root of the parsed program

        Raises:
            SyntacticAnalyzerError: If unexpected tokens remain after parsing
        """
        node: NodeAST = self._program()  # Parse complete program

        # Verify that all input has been consumed
        if self._current_token.type != TokenType.EOF:
            raise SyntacticError(
                ErrorCode.UNEXPECTED_TOKEN,
                "Unexpected token after program",
                self._current_token,
            )
        return node
