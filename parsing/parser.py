from typing import Union
from lexical_analysis.lexer import Lexer
from lexical_analysis.tokens import Token, TokenType
from parsing.ast import (
    NodeAST,
    NodeBlock,
    NodeFunctionDeclaration,
    NodeProcedureAndFunctionDeclarations,
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
    NodeVariableDeclaration,
)
from utils.exceptions import ParserError


class Parser:
    """
    Grammar (in Backus-Naur Form):
    program ::= PROGRAM variable SEMICOLON block DOT
    block ::= variable_declarations procedures_and_functions_declarations compound_statement
    variable_declarations ::= VAR (variable_declaration SEMICOLON)+ | empty
    variable_declaration ::= variable (COMMA variable)* COLON type
    procedures_and_functions_declarations ::= ((procedure_declaration | function_declaration) SEMICOLON)*
    procedure_declaration ::= PROCEDURE variable (LEFT_PARENTHESIS parameter_list RIGHT_PARENTHESIS)? SEMICOLON block
    function_declaration ::= FUNCTION variable (LEFT_PARENTHESIS parameter_list RIGHT_PARENTHESIS)? COLON type SEMICOLON block
    parameter_list ::= parameter (SEMICOLON parameter)*
    parameter ::= variable (COMMA variable)* COLON type
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

    __slots__ = ("lexer", "current_token")

    def __init__(self, lexer: Lexer) -> None:
        self.lexer: Lexer = lexer
        self.current_token: Token = self.lexer.next_token()

    def _consume(self, expected_type: TokenType) -> Token:
        if self.current_token.type == expected_type:
            token: Token = self.current_token
            self.current_token = self.lexer.next_token()
            return token
        else:
            raise ParserError(f"Expected {expected_type.value}", self.current_token)

    def _program(self) -> NodeProgram:
        self._consume(TokenType.PROGRAM)
        program_name: str = self._variable().id
        self._consume(TokenType.SEMICOLON)
        block: NodeBlock = self._block()
        self._consume(TokenType.DOT)
        return NodeProgram(program_name, block)

    def _block(self) -> NodeBlock:
        variable_declarations: Union[NodeVariableDeclarations, NodeEmpty] = (
            self._variable_declarations()
        )
        procedure_and_function_declarations: NodeProcedureAndFunctionDeclarations = (
            self._procedure_and_function_declarations()
        )
        compound_statement: NodeCompoundStatement = self._compound_statement()
        return NodeBlock(
            variable_declarations,
            procedure_and_function_declarations,
            compound_statement,
        )

    def _procedure_and_function_declarations(
        self,
    ) -> NodeProcedureAndFunctionDeclarations:
        procedure_and_function_declarations: list[
            Union[NodeProcedureDeclaration, NodeFunctionDeclaration]
        ] = []
        while self.current_token.type in (TokenType.PROCEDURE, TokenType.FUNCTION):
            if self.current_token.type == TokenType.PROCEDURE:
                procedure_and_function_declarations.append(
                    self._procedure_declaration()
                )
            else:
                procedure_and_function_declarations.append(self._function_declaration())
            self._consume(TokenType.SEMICOLON)
        return NodeProcedureAndFunctionDeclarations(procedure_and_function_declarations)

    def _procedure_declaration(self) -> NodeProcedureDeclaration:
        self._consume(TokenType.PROCEDURE)
        procedure_name: str = self._variable().id
        self._consume(TokenType.SEMICOLON)
        block: NodeBlock = self._block()
        return NodeProcedureDeclaration(procedure_name, block)

    def _function_declaration(self) -> NodeFunctionDeclaration:
        self._consume(TokenType.FUNCTION)
        function_name: str = self._variable().id
        self._consume(TokenType.SEMICOLON)
        block: NodeBlock = self._block()
        return NodeFunctionDeclaration(function_name, block)

    def _variable_declarations(self) -> Union[NodeVariableDeclarations, NodeEmpty]:
        if self.current_token.type == TokenType.VAR:
            self._consume(TokenType.VAR)
            variable_declarations: list[NodeVariableDeclaration] = []

            while self.current_token.type == TokenType.ID:
                variable_declarations.append(self._variable_declaration())
                self._consume(TokenType.SEMICOLON)

            return NodeVariableDeclarations(variable_declarations)
        else:
            return self._empty()

    def _variable_declaration(self) -> NodeVariableDeclaration:
        variables: list[NodeVariable] = [self._variable()]
        while self.current_token.type == TokenType.COMMA:
            self._consume(TokenType.COMMA)
            variables.append(self._variable())
        self._consume(TokenType.COLON)
        node_type: NodeType = self._type()
        return NodeVariableDeclaration(variables, node_type)

    def _type(self) -> NodeType:
        token: Token = self.current_token
        if token.type == TokenType.INTEGER:
            self._consume(TokenType.INTEGER)
            return NodeType(token)
        elif token.type == TokenType.REAL:
            self._consume(TokenType.REAL)
            return NodeType(token)
        else:
            raise ParserError("Expected INTEGER or REAL", token)

    def _statement(
        self,
    ) -> Union[NodeCompoundStatement, NodeAssignmentStatement, NodeEmpty]:
        if self.current_token.type == TokenType.BEGIN:
            return self._compound_statement()
        elif self.current_token.type == TokenType.ID:
            return self._assignment_statement()
        else:
            return self._empty()

    def _compound_statement(self) -> NodeCompoundStatement:
        self._consume(TokenType.BEGIN)
        children: list[
            Union[NodeCompoundStatement, NodeAssignmentStatement, NodeEmpty]
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
    ) -> list[Union[NodeCompoundStatement, NodeAssignmentStatement, NodeEmpty]]:
        nodes: list[
            Union[NodeCompoundStatement, NodeAssignmentStatement, NodeEmpty]
        ] = [self._statement()]
        while self.current_token.type == TokenType.SEMICOLON:
            self._consume(TokenType.SEMICOLON)
            nodes.append(self._statement())
        return nodes

    def _variable(self) -> NodeVariable:
        token: Token = self.current_token
        self._consume(TokenType.ID)
        return NodeVariable(token)

    def _factor(self) -> NodeAST:
        token: Token = self.current_token
        if token.type == TokenType.ID:
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
            raise ParserError("Expected number, unary operator, or '('", token)

    def _term(self) -> NodeAST:
        node: NodeAST = self._factor()
        while self.current_token.type in (
            TokenType.MUL,
            TokenType.TRUE_DIV,
            TokenType.INTEGER_DIV,
            TokenType.MOD,
        ):
            token: Token = self.current_token
            self._consume(token.type)
            right: NodeAST = self._factor()
            node = NodeBinaryOperation(node, token, right)
        return node

    def _expression(self) -> NodeAST:
        node: NodeAST = self._term()
        while self.current_token.type in (TokenType.PLUS, TokenType.MINUS):
            token: Token = self.current_token
            self._consume(token.type)
            right: NodeAST = self._term()
            node = NodeBinaryOperation(node, token, right)
        return node

    def parse(self) -> NodeAST:
        node: NodeAST = self._program()
        if self.current_token.type != TokenType.EOF:
            raise ParserError("Unexpected token after program", self.current_token)
        return node
