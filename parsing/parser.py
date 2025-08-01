from typing import Union
from lexical_analysis.lexer import Lexer
from lexical_analysis.tokens import Token, TokenType
from parsing.ast import (
    NodeAST,
    NodeEmptyStatement,
    NodeVariable,
    NodeAssignmentStatement,
    NodeCompoundStatement,
    NodeBinaryOperation,
    NodeNumber,
    NodeUnaryOperation,
)
from utils.exceptions import ParserError


class Parser:
    """Grammar (in Backus-Naur Form):
    program ::= compound_statement DOT
    compound_statement ::= BEGIN statement_list END
    statement_list ::= statement | statement SEMICOLON statement_list
    statement ::= compound_statement | assignment_statement | empty_statement
    assignment_statement ::= variable ASSIGN expression
    variable ::= ID
    empty_statement ::=
    expression ::= term ((PLUS | MINUS) term)*
    term ::= factor ((MUL | DIV) factor)*
    factor ::= (PLUS | MINUS)? (INTEGER | FLOAT | LEFT_PARENTHESIS expression RIGHT_PARENTHESIS | variable)
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

    def program(self) -> NodeCompoundStatement:
        node: NodeCompoundStatement = self.compound_statement()
        self.consume(TokenType.DOT)
        return node

    def statement(
        self,
    ) -> Union[NodeCompoundStatement, NodeAssignmentStatement, NodeEmptyStatement]:
        if self.current_token.type == TokenType.BEGIN:
            return self.compound_statement()
        elif self.current_token.type == TokenType.ID:
            return self.assignment_statement()
        else:
            return self.empty_statement()

    def compound_statement(self) -> NodeCompoundStatement:
        self.consume(TokenType.BEGIN)
        children: list[
            Union[NodeCompoundStatement, NodeAssignmentStatement, NodeEmptyStatement]
        ] = self.statement_list()
        self.consume(TokenType.END)
        return NodeCompoundStatement(children)

    def assignment_statement(self) -> NodeAssignmentStatement:
        variable: NodeVariable = self.variable()
        self.consume(TokenType.ASSIGN)
        return NodeAssignmentStatement(variable, self.expression())

    def empty_statement(self) -> NodeEmptyStatement:
        return NodeEmptyStatement()

    def statement_list(
        self,
    ) -> list[
        Union[NodeCompoundStatement, NodeAssignmentStatement, NodeEmptyStatement]
    ]:
        nodes: list[
            Union[NodeCompoundStatement, NodeAssignmentStatement, NodeEmptyStatement]
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
        elif token.type == TokenType.FLOAT:
            self.consume(TokenType.FLOAT)
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
