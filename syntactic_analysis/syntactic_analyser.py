from typing import Optional

from lexical_analysis.lexical_analyzer import LexicalAnalyzer
from lexical_analysis.tokens import Token, TokenType
from syntactic_analysis.ast import (
    NodeAST,
    NodeBlock,
    NodeProgram,
    NodeStatement,
    NodeExpression,
    NodeIdentifier,
    NodeType,
    NodeVariableDeclaration,
    NodeConstantDeclaration,
    NodeAssignment,
    NodeGiveStatement,
    NodeParameter,
    NodeFunctionDeclaration,
    NodeProcedureDeclaration,
    NodeFunctionCall,
    NodeProcedureCall,
    NodeBinaryOperation,
    NodeUnaryOperation,
    NodeIntegerLiteral,
    NodeFloatLiteral,
    NodeStringLiteral,
    NodeBooleanLiteral,
)
from utils.error_handling import SyntacticError, ErrorCode


class SyntacticAnalyzer:
    __slots__ = ("_lexical_analyzer", "_current_token")

    def __init__(self, lexer: LexicalAnalyzer) -> None:
        self._lexical_analyzer = lexer
        self._current_token = lexer.next_token()

    def parse(self) -> NodeAST:
        node = self._program()
        if self._current_token.type != TokenType.EOF:
            raise SyntacticError(
                ErrorCode.UNEXPECTED_TOKEN,
                f"Expected EOF, got {self._current_token.type.value}",
                self._current_token,
            )
        return node

    def _consume(self, expected_type: TokenType) -> Token:
        if self._current_token.type == expected_type:
            token = self._current_token
            self._current_token = self._lexical_analyzer.next_token()
            return token
        raise SyntacticError(
            ErrorCode.UNEXPECTED_TOKEN,
            f"Expected {expected_type.value}, got {self._current_token.type.value}",
            self._current_token,
        )

    def _peek_next_token(self) -> Token:
        pos, char = self._lexical_analyzer.position, self._lexical_analyzer.current_char
        line, col = self._lexical_analyzer.line, self._lexical_analyzer.column

        next_token = self._lexical_analyzer.next_token()

        self._lexical_analyzer.position = pos
        self._lexical_analyzer.current_char = char
        self._lexical_analyzer.line = line
        self._lexical_analyzer.column = col

        return next_token

    def _program(self) -> NodeProgram:
        return NodeProgram(self._block())

    def _block(self) -> NodeBlock:
        self._consume(TokenType.LEFT_BRACE)
        while self._current_token.type == TokenType.NEWLINE:
            self._consume(TokenType.NEWLINE)

        statements: list[NodeStatement] = []

        while self._current_token.type != TokenType.RIGHT_BRACE:
            statements.append(self._statement())
            self._consume(TokenType.NEWLINE)
            while self._current_token.type == TokenType.NEWLINE:
                self._consume(TokenType.NEWLINE)

        self._consume(TokenType.RIGHT_BRACE)
        return NodeBlock(statements)

    def _statement(self) -> NodeStatement:
        match self._current_token.type:
            case TokenType.LET:
                return self._variable_declaration()
            case TokenType.KEEP:
                return self._constant_declaration()
            case TokenType.FUNC:
                return self._function_declaration()
            case TokenType.PROC:
                return self._procedure_declaration()
            case TokenType.EXEC:
                return self._procedure_call()
            case TokenType.GIVE:
                return self._give_statement()
            case TokenType.IDENTIFIER:
                next_token = self._peek_next_token()
                if next_token.type == TokenType.LEFT_PARENTHESIS:
                    return self._function_call()
                if next_token.type == TokenType.ASSIGN:
                    return self._assignment()
                return self._function_call()
            case _:
                raise SyntacticError(
                    ErrorCode.UNEXPECTED_TOKEN,
                    f"Expected statement, got {self._current_token.type.value}",
                    self._current_token,
                )

    def _variable_declaration(self) -> NodeVariableDeclaration:
        self._consume(TokenType.LET)
        var_type = self._type()
        identifiers = self._identifier_list()
        expressions: Optional[list[NodeExpression]] = None

        if self._current_token.type == TokenType.ASSIGN:
            self._consume(TokenType.ASSIGN)
            expressions = self._expression_list()
            if len(identifiers) != len(expressions):
                raise SyntacticError(
                    ErrorCode.WRONG_NUMBER_OF_EXPRESSIONS,
                    f"Expected {len(identifiers)} expressions, got {len(expressions)}",
                    self._current_token,
                )

        return NodeVariableDeclaration(var_type, identifiers, expressions)

    def _constant_declaration(self) -> NodeConstantDeclaration:
        self._consume(TokenType.KEEP)
        const_type = self._type()
        identifiers = self._identifier_list()
        self._consume(TokenType.ASSIGN)
        expressions = self._expression_list()

        if len(identifiers) != len(expressions):
            raise SyntacticError(
                ErrorCode.WRONG_NUMBER_OF_EXPRESSIONS,
                f"Expected {len(identifiers)} expressions, got {len(expressions)}",
                self._current_token,
            )

        return NodeConstantDeclaration(const_type, identifiers, expressions)

    def _function_declaration(self) -> NodeFunctionDeclaration:
        self._consume(TokenType.FUNC)
        name = self._identifier()
        self._consume(TokenType.LEFT_PARENTHESIS)

        parameters: Optional[list[NodeParameter]] = None
        if self._current_token.type != TokenType.RIGHT_PARENTHESIS:
            parameters = self._parameter_list()

        self._consume(TokenType.RIGHT_PARENTHESIS)
        return_type = self._return_type()
        block = self._block()
        return NodeFunctionDeclaration(name, parameters, return_type, block)

    def _procedure_declaration(self) -> NodeProcedureDeclaration:
        self._consume(TokenType.PROC)
        name = self._identifier()
        self._consume(TokenType.LEFT_PARENTHESIS)

        parameters: Optional[list[NodeParameter]] = None
        if self._current_token.type != TokenType.RIGHT_PARENTHESIS:
            parameters = self._parameter_list()

        self._consume(TokenType.RIGHT_PARENTHESIS)
        block = self._block()
        return NodeProcedureDeclaration(name, parameters, block)

    def _assignment(self) -> NodeAssignment:
        identifier = self._identifier()
        self._consume(TokenType.ASSIGN)
        expression = self._expression()
        return NodeAssignment(identifier, expression)

    def _function_call(self) -> NodeFunctionCall:
        name = self._identifier()
        self._consume(TokenType.LEFT_PARENTHESIS)

        arguments: Optional[list[NodeExpression]] = None
        if self._current_token.type != TokenType.RIGHT_PARENTHESIS:
            arguments = self._argument_list()

        self._consume(TokenType.RIGHT_PARENTHESIS)
        return NodeFunctionCall(name, arguments)

    def _procedure_call(self) -> NodeProcedureCall:
        self._consume(TokenType.EXEC)
        name = self._identifier()
        self._consume(TokenType.LEFT_PARENTHESIS)

        arguments: Optional[list[NodeExpression]] = None
        if self._current_token.type != TokenType.RIGHT_PARENTHESIS:
            arguments = self._argument_list()

        self._consume(TokenType.RIGHT_PARENTHESIS)
        return NodeProcedureCall(name, arguments)

    def _give_statement(self) -> NodeGiveStatement:
        self._consume(TokenType.GIVE)
        if self._current_token.type in (TokenType.NEWLINE, TokenType.RIGHT_BRACE):
            return NodeGiveStatement(None)
        return NodeGiveStatement(self._expression())

    def _identifier_list(self) -> list[NodeIdentifier]:
        identifiers = [self._identifier()]
        while self._current_token.type == TokenType.COMMA:
            self._consume(TokenType.COMMA)
            identifiers.append(self._identifier())
        return identifiers

    def _expression_list(self) -> list[NodeExpression]:
        expressions = [self._expression()]
        while self._current_token.type == TokenType.COMMA:
            self._consume(TokenType.COMMA)
            expressions.append(self._expression())
        return expressions

    def _parameter_list(self) -> list[NodeParameter]:
        parameters = [self._parameter()]
        while self._current_token.type == TokenType.COMMA:
            self._consume(TokenType.COMMA)
            parameters.append(self._parameter())
        return parameters

    def _argument_list(self) -> list[NodeExpression]:
        arguments = [self._expression()]
        while self._current_token.type == TokenType.COMMA:
            self._consume(TokenType.COMMA)
            arguments.append(self._expression())
        return arguments

    def _parameter(self) -> NodeParameter:
        identifier = self._identifier()
        self._consume(TokenType.COLON)
        param_type = self._type()
        return NodeParameter(identifier, param_type)

    def _return_type(self) -> NodeType:
        self._consume(TokenType.ARROW)
        return self._type()

    def _type(self) -> NodeType:
        token = self._current_token
        if token.type in {
            TokenType.INT_TYPE,
            TokenType.FLOAT_TYPE,
            TokenType.STRING_TYPE,
            TokenType.BOOL_TYPE,
        }:
            self._consume(token.type)
            return NodeType(token)

        raise SyntacticError(
            ErrorCode.UNEXPECTED_TOKEN,
            f"Expected type, got {token.type.value}",
            token,
        )

    def _identifier(self) -> NodeIdentifier:
        token = self._consume(TokenType.IDENTIFIER)
        return NodeIdentifier(token.value)

    def _expression(self) -> NodeExpression:
        return self._additive_expression()

    def _additive_expression(self) -> NodeExpression:
        left = self._multiplicative_expression()
        while self._current_token.type in {TokenType.PLUS, TokenType.MINUS}:
            op = self._current_token
            self._consume(op.type)
            right = self._multiplicative_expression()
            left = NodeBinaryOperation(left, op.value, right)
        return left

    def _multiplicative_expression(self) -> NodeExpression:
        left = self._power_expression()
        while self._current_token.type in {
            TokenType.MULTIPLY,
            TokenType.DIVIDE,
            TokenType.FLOOR_DIVIDE,
            TokenType.MODULO,
        }:
            op = self._current_token
            self._consume(op.type)
            right = self._power_expression()
            left = NodeBinaryOperation(left, op.value, right)
        return left

    def _power_expression(self) -> NodeExpression:
        left = self._unary_expression()
        if self._current_token.type == TokenType.POWER:
            op = self._current_token
            self._consume(TokenType.POWER)
            right = self._unary_expression()
            return NodeBinaryOperation(left, op.value, right)
        return left

    def _unary_expression(self) -> NodeExpression:
        if self._current_token.type in {TokenType.PLUS, TokenType.MINUS}:
            op = self._current_token
            self._consume(op.type)
            operand = self._primary_expression()
            return NodeUnaryOperation(op.value, operand)
        return self._primary_expression()

    def _primary_expression(self) -> NodeExpression:
        token = self._current_token

        if token.type == TokenType.INT_LITERAL:
            self._consume(TokenType.INT_LITERAL)
            return NodeIntegerLiteral(token.value)

        if token.type == TokenType.FLOAT_LITERAL:
            self._consume(TokenType.FLOAT_LITERAL)
            return NodeFloatLiteral(token.value)

        if token.type == TokenType.STRING_LITERAL:
            self._consume(TokenType.STRING_LITERAL)
            return NodeStringLiteral(token.value)

        if token.type == TokenType.BOOL_LITERAL:
            self._consume(TokenType.BOOL_LITERAL)
            return NodeBooleanLiteral(token.value)

        if token.type == TokenType.IDENTIFIER:
            next_token = self._peek_next_token()
            if next_token.type == TokenType.LEFT_PARENTHESIS:
                return self._function_call()
            return self._identifier()

        if token.type == TokenType.LEFT_PARENTHESIS:
            self._consume(TokenType.LEFT_PARENTHESIS)
            expr = self._expression()
            self._consume(TokenType.RIGHT_PARENTHESIS)
            return expr

        raise SyntacticError(
            ErrorCode.UNEXPECTED_TOKEN,
            f"Expected expression, got {token.type.value}",
            token,
        )
