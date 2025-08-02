from typing import Union
from lexical_analysis.lexer import Lexer
from lexical_analysis.tokens import Token, TokenType
from parsing.ast import (
    NodeAST,
    NodeDeclarations,
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
        program ::= PROGRAM variable SEMICOLON declarations compound_statement DOT
        declarations ::= VAR (variable_declaration SEMICOLON)+ | empty
        variable_declaration ::= variable (COMMA variable)* COLON type
        variable ::= ID
        type ::= INTEGER | REAL
        compound_statement ::= BEGIN statement_list END
        statement_list ::= statement | statement SEMICOLON statement_list
        statement ::= compound_statement | assignment_statement | empty
        assignment_statement ::= variable ASSIGN expression
        empty ::=
        expression ::= term ((PLUS | MINUS) term)*
        term ::= factor ((MUL | TRUE_DIV | INTEGER_DIV | MOD) factor)*
        factor ::= (PLUS | MINUS)? (INTEGER | REAL | LEFT_PARENTHESIS expression RIGHT_PARENTHESIS | variable)
    """

    __slots__ = ("lexer", "current_token")

    def __init__(self, lexer: Lexer) -> None:
        self.lexer: Lexer = lexer
        self.current_token: Token = self.lexer.next_token()

    def consume(self, expected_type: TokenType) -> Token:
        if self.current_token.type == expected_type:
            token: Token = self.current_token
            self.current_token = self.lexer.next_token()
            return token
        else:
            raise ParserError(f"Expected {expected_type.value}", self.current_token)

    def program(self) -> NodeProgram:
        self.consume(TokenType.PROGRAM)
        program_name: str = self.variable().id
        self.consume(TokenType.SEMICOLON)
        variable_declaration_section: Union[NodeDeclarations, NodeEmpty] = (
            self.declarations()
        )
        main_block: NodeCompoundStatement = self.compound_statement()
        self.consume(TokenType.DOT)
        return NodeProgram(program_name, variable_declaration_section, main_block)

    def declarations(self) -> Union[NodeDeclarations, NodeEmpty]:
        if self.current_token.type == TokenType.VAR:
            self.consume(TokenType.VAR)
            declarations: list[NodeVariableDeclaration] = [self.variable_declaration()]
            while self.current_token.type == TokenType.SEMICOLON:  # type: ignore
                self.consume(TokenType.SEMICOLON)
                if self.current_token.type == TokenType.ID:
                    declarations.append(self.variable_declaration())
            return NodeDeclarations(declarations)
        else:
            return self.empty()

    def variable_declaration(self) -> NodeVariableDeclaration:
        variables: list[NodeVariable] = [self.variable()]
        while self.current_token.type == TokenType.COMMA:
            self.consume(TokenType.COMMA)
            variables.append(self.variable())
        self.consume(TokenType.COLON)
        type: NodeType = self.type()
        return NodeVariableDeclaration(variables, type)

    def type(self) -> NodeType:
        token: Token = self.current_token
        if token.type == TokenType.INTEGER_TYPE:
            self.consume(TokenType.INTEGER_TYPE)
        elif token.type == TokenType.REAL_TYPE:
            self.consume(TokenType.REAL_TYPE)
        else:
            raise ParserError(f"Expected INTEGER_TYPE or REAL_TYPE", token)
        return NodeType(token)

    def statement(
        self,
    ) -> Union[NodeCompoundStatement, NodeAssignmentStatement, NodeEmpty]:
        if self.current_token.type == TokenType.BEGIN:
            return self.compound_statement()
        elif self.current_token.type == TokenType.ID:
            return self.assignment_statement()
        else:
            return self.empty()

    def compound_statement(self) -> NodeCompoundStatement:
        self.consume(TokenType.BEGIN)
        children: list[
            Union[NodeCompoundStatement, NodeAssignmentStatement, NodeEmpty]
        ] = self.statement_list()
        self.consume(TokenType.END)
        return NodeCompoundStatement(children)

    def assignment_statement(self) -> NodeAssignmentStatement:
        variable: NodeVariable = self.variable()
        self.consume(TokenType.ASSIGN)
        return NodeAssignmentStatement(variable, self.expression())

    def empty(self) -> NodeEmpty:
        return NodeEmpty()

    def statement_list(
        self,
    ) -> list[Union[NodeCompoundStatement, NodeAssignmentStatement, NodeEmpty]]:
        nodes: list[
            Union[NodeCompoundStatement, NodeAssignmentStatement, NodeEmpty]
        ] = [self.statement()]
        while self.current_token.type == TokenType.SEMICOLON:
            self.consume(TokenType.SEMICOLON)
            nodes.append(self.statement())
        return nodes

    def variable(self) -> NodeVariable:
        token: Token = self.current_token
        self.consume(TokenType.ID)
        return NodeVariable(token)

    def factor(self) -> NodeAST:
        token: Token = self.current_token
        if token.type == TokenType.ID:
            return self.variable()
        elif token.type == TokenType.INTEGER:
            self.consume(TokenType.INTEGER)
            return NodeNumber(token)
        elif token.type == TokenType.REAL:
            self.consume(TokenType.REAL)
            return NodeNumber(token)
        elif token.type == TokenType.LEFT_PARENTHESIS:
            self.consume(TokenType.LEFT_PARENTHESIS)
            node = self.expression()
            self.consume(TokenType.RIGHT_PARENTHESIS)
            return node
        elif token.type in (TokenType.PLUS, TokenType.MINUS):
            self.consume(token.type)
            operand = self.factor()
            return NodeUnaryOperation(token, operand)
        else:
            raise ParserError("Expected number, unary operator, or '('", token)

    def term(self) -> NodeAST:
        node: NodeAST = self.factor()
        while self.current_token.type in (
            TokenType.MUL,
            TokenType.TRUE_DIV,
            TokenType.INTEGER_DIV,
            TokenType.MOD,
        ):
            token: Token = self.current_token
            self.consume(token.type)
            right: NodeAST = self.factor()
            node = NodeBinaryOperation(node, token, right)
        return node

    def expression(self) -> NodeAST:
        node: NodeAST = self.term()
        while self.current_token.type in (TokenType.PLUS, TokenType.MINUS):
            token: Token = self.current_token
            self.consume(token.type)
            right: NodeAST = self.term()
            node = NodeBinaryOperation(node, token, right)
        return node

    def parse(self) -> NodeAST:
        node: NodeAST = self.program()
        if self.current_token.type != TokenType.EOF:
            raise ParserError("Unexpected token after expression", self.current_token)
        return node
