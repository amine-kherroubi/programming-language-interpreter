from typing import Union
from lexical_analysis.lexical_analyzer import LexicalAnalyzer
from lexical_analysis.tokens import Token, TokenType
from syntactic_analysis.ast import (
    NodeAST,
    NodeBlock,
    NodeFunctionCall,
    NodeFunctionDeclaration,
    NodeParameterGroup,
    NodeProcedureCall,
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
    statement ::= compound_statement | assignment_statement | procedure_call | empty
    assignment_statement ::= variable ASSIGN expression
    procedure_call ::= variable LEFT_PARENTHESIS arguments? RIGHT_PARENTHESIS
    function_call ::= variable LEFT_PARENTHESIS arguments? RIGHT_PARENTHESIS
    arguments ::= expression (COMMA expression)*
    expression ::= term ((PLUS | MINUS) term)*
    term ::= factor ((MUL | TRUE_DIV | DIV | MOD) factor)*
    factor ::= (PLUS | MINUS)? (INTEGER_CONSTANT | REAL_CONSTANT | LEFT_PARENTHESIS expression RIGHT_PARENTHESIS | variable | function_call)
    variable ::= ID
    empty ::=
    """

    __slots__ = ("_lexical_analyzer", "_current_token")

    def __init__(self, lexer: LexicalAnalyzer) -> None:
        self._lexical_analyzer: LexicalAnalyzer = lexer
        self._current_token: Token = self._lexical_analyzer.next_token()

    def _consume(self, expected_type: TokenType) -> Token:
        if self._current_token.type == expected_type:
            token: Token = self._current_token
            self._current_token = self._lexical_analyzer.next_token()
            return token
        else:
            raise SyntacticError(
                ErrorCode.UNEXPECTED_TOKEN,
                f"Expected {expected_type.value}",
                self._current_token,
            )

    def _program(self) -> NodeProgram:
        self._consume(TokenType.PROGRAM)
        program_name: str = self._variable().name
        self._consume(TokenType.SEMICOLON)
        block: NodeBlock = self._block()
        self._consume(TokenType.DOT)
        return NodeProgram(program_name, block)

    def _block(self) -> NodeBlock:
        variable_declarations: Union[NodeVariableDeclarations, NodeEmpty] = (
            self._variable_declarations()
        )
        subroutine_declarations: NodeSubroutineDeclarations = (
            self._subroutine_declarations()
        )
        compound_statement: NodeCompoundStatement = self._compound_statement()
        return NodeBlock(
            variable_declarations,
            subroutine_declarations,
            compound_statement,
        )

    def _subroutine_declarations(
        self,
    ) -> NodeSubroutineDeclarations:
        subroutine_declarations: list[
            Union[NodeProcedureDeclaration, NodeFunctionDeclaration]
        ] = []
        while self._current_token.type in (TokenType.PROCEDURE, TokenType.FUNCTION):
            if self._current_token.type == TokenType.PROCEDURE:
                subroutine_declarations.append(self._procedure_declaration())
            else:
                subroutine_declarations.append(self._function_declaration())
            self._consume(TokenType.SEMICOLON)
        return NodeSubroutineDeclarations(subroutine_declarations)

    def _procedure_declaration(self) -> NodeProcedureDeclaration:
        self._consume(TokenType.PROCEDURE)
        procedure_name: str = self._variable().name
        parameters: Union[NodeEmpty, list[NodeParameterGroup]] = NodeEmpty()
        if self._current_token.type == TokenType.LEFT_PARENTHESIS:
            self._consume(TokenType.LEFT_PARENTHESIS)
            parameters = self._parameters()
            self._consume(TokenType.RIGHT_PARENTHESIS)
        self._consume(TokenType.SEMICOLON)
        block: NodeBlock = self._block()
        return NodeProcedureDeclaration(procedure_name, parameters, block)

    def _function_declaration(self) -> NodeFunctionDeclaration:
        self._consume(TokenType.FUNCTION)
        function_name: str = self._variable().name
        parameters: Union[NodeEmpty, list[NodeParameterGroup]] = NodeEmpty()
        if self._current_token.type == TokenType.LEFT_PARENTHESIS:
            self._consume(TokenType.LEFT_PARENTHESIS)
            parameters = self._parameters()
            self._consume(TokenType.RIGHT_PARENTHESIS)
        self._consume(TokenType.COLON)
        return_type: NodeType = self._type()
        self._consume(TokenType.SEMICOLON)
        block: NodeBlock = self._block()
        return NodeFunctionDeclaration(function_name, parameters, return_type, block)

    def _parameters(self) -> list[NodeParameterGroup]:
        parameters: list[NodeParameterGroup] = [self._parameter_group()]
        while self._current_token.type == TokenType.SEMICOLON:
            self._consume(TokenType.SEMICOLON)
            parameters.append(self._parameter_group())
        return parameters

    def _parameter_group(self) -> NodeParameterGroup:
        variables: list[NodeVariable] = [self._variable()]
        while self._current_token.type == TokenType.COMMA:
            self._consume(TokenType.COMMA)
            variables.append(self._variable())
        self._consume(TokenType.COLON)
        type: NodeType = self._type()
        return NodeParameterGroup(variables, type)

    def _variable_declarations(self) -> Union[NodeVariableDeclarations, NodeEmpty]:
        if self._current_token.type == TokenType.VAR:
            self._consume(TokenType.VAR)
            variable_declarations: list[NodeVariableDeclarationGroup] = []
            while self._current_token.type == TokenType.ID:
                variable_declarations.append(self._variable_declaration())
                self._consume(TokenType.SEMICOLON)
            return NodeVariableDeclarations(variable_declarations)
        else:
            return self._empty()

    def _variable_declaration(self) -> NodeVariableDeclarationGroup:
        variables: list[NodeVariable] = [self._variable()]
        while self._current_token.type == TokenType.COMMA:
            self._consume(TokenType.COMMA)
            variables.append(self._variable())
        self._consume(TokenType.COLON)
        node_type: NodeType = self._type()
        return NodeVariableDeclarationGroup(variables, node_type)

    def _type(self) -> NodeType:
        token: Token = self._current_token
        if token.type == TokenType.INTEGER:
            self._consume(TokenType.INTEGER)
            return NodeType(token)
        elif token.type == TokenType.REAL:
            self._consume(TokenType.REAL)
            return NodeType(token)
        else:
            raise SyntacticError(
                ErrorCode.UNEXPECTED_TOKEN, "Expected INTEGER or REAL", token
            )

    def _statement(
        self,
    ) -> Union[
        NodeCompoundStatement, NodeProcedureCall, NodeAssignmentStatement, NodeEmpty
    ]:
        if self._current_token.type == TokenType.BEGIN:
            return self._compound_statement()
        elif (
            self._current_token.type == TokenType.ID
            and self._lexical_analyzer.current_char == "("
        ):
            return self._procedure_call()
        elif self._current_token.type == TokenType.ID:
            return self._assignment_statement()
        else:
            return self._empty()

    def _compound_statement(self) -> NodeCompoundStatement:
        self._consume(TokenType.BEGIN)
        children: list[
            Union[
                NodeCompoundStatement,
                NodeProcedureCall,
                NodeAssignmentStatement,
                NodeEmpty,
            ]
        ] = self._statement_list()
        self._consume(TokenType.END)
        return NodeCompoundStatement(children)

    def _assignment_statement(self) -> NodeAssignmentStatement:
        _variable: NodeVariable = self._variable()
        self._consume(TokenType.ASSIGN)
        return NodeAssignmentStatement(_variable, self._expression())

    def _empty(self) -> NodeEmpty:
        return NodeEmpty()

    def _statement_list(
        self,
    ) -> list[
        Union[
            NodeCompoundStatement, NodeProcedureCall, NodeAssignmentStatement, NodeEmpty
        ]
    ]:
        nodes: list[
            Union[
                NodeCompoundStatement,
                NodeProcedureCall,
                NodeAssignmentStatement,
                NodeEmpty,
            ]
        ] = [self._statement()]
        while self._current_token.type == TokenType.SEMICOLON:
            self._consume(TokenType.SEMICOLON)
            nodes.append(self._statement())
        return nodes

    def _variable(self) -> NodeVariable:
        token: Token = self._current_token
        self._consume(TokenType.ID)
        return NodeVariable(token)

    def _factor(self) -> NodeAST:
        token: Token = self._current_token
        if token.type == TokenType.ID and self._lexical_analyzer.current_char == "(":
            return self._function_call()
        elif token.type == TokenType.ID:
            return self._variable()
        elif token.type == TokenType.INTEGER_CONSTANT:
            self._consume(TokenType.INTEGER_CONSTANT)
            return NodeNumber(token)
        elif token.type == TokenType.REAL_CONSTANT:
            self._consume(TokenType.REAL_CONSTANT)
            return NodeNumber(token)
        elif token.type == TokenType.LEFT_PARENTHESIS:
            self._consume(TokenType.LEFT_PARENTHESIS)
            node: NodeAST = self._expression()
            self._consume(TokenType.RIGHT_PARENTHESIS)
            return node
        elif token.type in (TokenType.PLUS, TokenType.MINUS):
            self._consume(token.type)
            operand: NodeAST = self._factor()
            return NodeUnaryOperation(token, operand)
        else:
            raise SyntacticError(
                ErrorCode.UNEXPECTED_TOKEN,
                "Expected number, unary operator, or '('",
                token,
            )

    def _term(self) -> NodeAST:
        node: NodeAST = self._factor()
        while self._current_token.type in (
            TokenType.MUL,
            TokenType.DIV,
            TokenType.TRUE_DIV,
            TokenType.MOD,
        ):
            token: Token = self._current_token
            self._consume(token.type)
            right: NodeAST = self._factor()
            node = NodeBinaryOperation(node, token, right)
        return node

    def _expression(self) -> NodeAST:
        node: NodeAST = self._term()
        while self._current_token.type in (TokenType.PLUS, TokenType.MINUS):
            token: Token = self._current_token
            self._consume(token.type)
            right: NodeAST = self._term()
            node = NodeBinaryOperation(node, token, right)
        return node

    def _procedure_call(self) -> NodeProcedureCall:
        procedure_name: str = self._variable().name
        arguments: Union[NodeEmpty, list[NodeAST]] = self._empty()
        self._consume(TokenType.LEFT_PARENTHESIS)
        if self._current_token.type != TokenType.RIGHT_PARENTHESIS:
            arguments = self._arguments()
        self._consume(TokenType.RIGHT_PARENTHESIS)
        return NodeProcedureCall(procedure_name, arguments)

    def _function_call(self) -> NodeFunctionCall:
        function_name: str = self._variable().name
        arguments: Union[NodeEmpty, list[NodeAST]] = self._empty()
        self._consume(TokenType.LEFT_PARENTHESIS)
        if self._current_token.type != TokenType.RIGHT_PARENTHESIS:
            arguments = self._arguments()
        self._consume(TokenType.RIGHT_PARENTHESIS)
        return NodeFunctionCall(function_name, arguments)

    def _arguments(self) -> list[NodeAST]:
        arguments: list[NodeAST] = [self._expression()]
        while self._current_token.type == TokenType.COMMA:
            self._consume(TokenType.COMMA)
            arguments.append(self._expression())
        return arguments

    def parse(self) -> NodeAST:
        node: NodeAST = self._program()
        if self._current_token.type != TokenType.EOF:
            raise SyntacticError(
                ErrorCode.UNEXPECTED_TOKEN,
                "Unexpected token after program",
                self._current_token,
            )
        return node
