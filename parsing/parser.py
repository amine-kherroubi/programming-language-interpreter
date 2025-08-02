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
        variable_declaration_section: Union[NodeDeclarations, NodeEmpty]
        self._consume(TokenType.SEMICOLON)
        variable_declaration_section = self._declarations()
        main_block: NodeCompoundStatement = self._compound_statement()
        self._consume(TokenType.DOT)
        return NodeProgram(program_name, variable_declaration_section, main_block)

    def _declarations(self) -> Union[NodeDeclarations, NodeEmpty]:
        if self.current_token.type == TokenType.VAR:
            self._consume(TokenType.VAR)
            declarations: list[NodeVariableDeclaration] = [self._variable_declaration()]
            while self.current_token.type == TokenType.SEMICOLON:
                self._consume(TokenType.SEMICOLON)
                if self.current_token.type == TokenType.ID:
                    declarations.append(self._variable_declaration())
            return NodeDeclarations(declarations)
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
        if token.type == TokenType.INTEGER_TYPE:
            self._consume(TokenType.INTEGER_TYPE)
        elif token.type == TokenType.REAL_TYPE:
            self._consume(TokenType.REAL_TYPE)
        else:
            raise ParserError("Expected INTEGER_TYPE or REAL_TYPE", token)
        return NodeType(token)

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
        elif token.type == TokenType.INTEGER:
            self._consume(TokenType.INTEGER)
            return NodeNumber(token)
        elif token.type == TokenType.REAL:
            self._consume(TokenType.REAL)
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
            raise ParserError("Unexpected token after _expression", self.current_token)
        return node
