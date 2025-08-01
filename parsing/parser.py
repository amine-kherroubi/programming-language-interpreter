from typing import Union
from lexical_analysis.lexer import Lexer
from lexical_analysis.tokens import Token, TokenType
from parsing.ast import (
    NodeAST,
    NodeNoOp,
    NodeVar,
    NodeAssign,
    NodeCompoundStatement,
    NodeBinaryOp,
    NodeNumber,
    NodeUnaryOp,
)
from utils.exceptions import ParserError


class Parser:
    """Grammar (in Backus-Naur Form):
    program ::= compound_statement DOT
    compound_statement ::= START statement_list END
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

    def statement(self) -> Union[NodeCompoundStatement, NodeAssign, NodeNoOp]:
        if self.current_token.type == TokenType.START:
            return self.compound_statement()
        elif self.current_token.type == TokenType.ID:
            return self.assignment_statement()
        else:
            return self.empty_statement()

    def compound_statement(self) -> NodeCompoundStatement:
        self.consume(TokenType.START)
        children: list[Union[NodeCompoundStatement, NodeAssign, NodeNoOp]] = (
            self.statement_list()
        )
        self.consume(TokenType.END)
        return NodeCompoundStatement(children)

    def assignment_statement(self) -> NodeAssign:
        variable: NodeVar = self.variable()
        self.consume(TokenType.ASSIGN)
        return NodeAssign(variable, self.expression())

    def empty_statement(self) -> NodeNoOp:
        return NodeNoOp()

    def statement_list(
        self,
    ) -> list[Union[NodeCompoundStatement, NodeAssign, NodeNoOp]]:
        nodes: list[Union[NodeCompoundStatement, NodeAssign, NodeNoOp]] = [
            self.statement()
        ]
        while self.current_token.type == TokenType.SEMICOLON:
            self.consume(TokenType.SEMICOLON)
            nodes.append(self.statement())
        if self.current_token.type == TokenType.ID:
            pass
        return nodes

    def variable(self) -> NodeVar:
        token: Token = self.current_token
        self.consume(TokenType.ID)
        return NodeVar(token)

    def factor(self) -> NodeAST:
        token: Token = self.current_token
        if token.type == TokenType.ID:
            self.consume(TokenType.ID)
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
            return NodeUnaryOp(token, operand)
        else:
            raise ParserError("Expected number, unary operator, or '('", token)

    def term(self) -> NodeAST:
        node: NodeAST = self.factor()
        while self.current_token.type in (TokenType.MUL, TokenType.DIV):
            token: Token = self.current_token
            self.consume(token.type)
            right: NodeAST = self.factor()
            node = NodeBinaryOp(node, token, right)
        return node

    def expression(self) -> NodeAST:
        node: NodeAST = self.term()
        while self.current_token.type in (TokenType.PLUS, TokenType.MINUS):
            token: Token = self.current_token
            self.consume(token.type)
            right: NodeAST = self.term()
            node = NodeBinaryOp(node, token, right)
        return node

    def parse(self) -> NodeAST:
        node: NodeAST = self.program()
        if self.current_token.type != TokenType.EOF:
            raise ParserError("Unexpected token after expression", self.current_token)
        return node
