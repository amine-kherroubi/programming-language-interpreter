from lexical_analysis.lexer import Lexer
from lexical_analysis.tokens import Token, TokenType
from parsing.ast import NodeAST, NodeBinaryOp, NodeNumber, NodeUnaryOp
from utils.exceptions import ParserError


class Parser:
    """Recursive descent parser for mathematical expressions

    Grammar (BNF):
    expression ::= term ((PLUS | MINUS) term)*
    term ::= factor ((MUL | DIV) factor)*
    factor ::= (PLUS | MINUS)? (INTEGER | FLOAT | '(' expression ')')
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

    def factor(self) -> NodeAST:
        token: Token = self.current_token
        if token.type == TokenType.INTEGER:
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
            node = NodeBinaryOp(left=node, token=token, right=right)
        return node

    def expression(self) -> NodeAST:
        node: NodeAST = self.term()
        while self.current_token.type in (TokenType.PLUS, TokenType.MINUS):
            token: Token = self.current_token
            self.consume(token.type)
            right: NodeAST = self.term()
            node = NodeBinaryOp(left=node, token=token, right=right)
        return node

    def parse(self) -> NodeAST:
        node: NodeAST = self.expression()
        if self.current_token.type != TokenType.EOF:
            raise ParserError("Unexpected token after expression", self.current_token)
        return node
