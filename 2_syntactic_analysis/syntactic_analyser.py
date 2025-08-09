from typing import Optional
from lexical_analysis.lexical_analyzer import LexicalAnalyzer
from lexical_analysis.tokens import Token, TokenType
from syntactic_analysis.ast import (
    NodeAST,
    NodeArithmeticExpressionAsBoolean,
    NodeBinaryBooleanOperation,
    NodeBlock,
    NodeBooleanExpression,
    NodeComparison,
    NodeElif,
    NodeElse,
    NodeExpression,
    NodeIfStatement,
    NodeProgram,
    NodeShowStatement,
    NodeSkipStatement,
    NodeStatement,
    NodeArithmeticExpression,
    NodeIdentifier,
    NodeStopStatement,
    NodeType,
    NodeUnaryBooleanOperation,
    NodeVariableDeclaration,
    NodeConstantDeclaration,
    NodeAssignmentStatement,
    NodeGiveStatement,
    NodeParameter,
    NodeFunctionDeclaration,
    NodeProcedureDeclaration,
    NodeFunctionCall,
    NodeProcedureCall,
    NodeBinaryArithmeticOperation,
    NodeUnaryArithmeticOperation,
    NodeIntegerLiteral,
    NodeFloatLiteral,
    NodeStringLiteral,
    NodeBooleanLiteral,
    NodeWhileStatement,
)
from utils.errors import SyntacticError, ErrorCode


class SyntacticAnalyzer:
    __slots__ = ("_lexical_analyzer", "_current_token")

    def __init__(self, lexer: LexicalAnalyzer) -> None:
        self._lexical_analyzer: LexicalAnalyzer = lexer
        self._current_token: Token = lexer.next_token()

    def parse(self) -> NodeAST:
        node: NodeProgram = self._program()
        if self._current_token.type != TokenType.EOF:
            raise SyntacticError(
                ErrorCode.UNEXPECTED_TOKEN,
                f"Expected EOF, got {self._current_token.type.value}",
                self._current_token,
            )
        return node

    def _consume(self, expected_type: TokenType) -> Token:
        if self._current_token.type == expected_type:
            token: Token = self._current_token
            self._current_token = self._lexical_analyzer.next_token()
            return token
        raise SyntacticError(
            ErrorCode.UNEXPECTED_TOKEN,
            f"Expected {expected_type.value}, got {self._current_token.type.value}",
            self._current_token,
        )

    def _peek_next_token(self) -> Token:
        lookahead_position: int = self._lexical_analyzer.position
        lookahead_character: Optional[str] = self._lexical_analyzer.current_char
        lookahead_line: int = self._lexical_analyzer.line
        lookahead_column: int = self._lexical_analyzer.column

        next_token: Token = self._lexical_analyzer.next_token()

        self._lexical_analyzer.position = lookahead_position
        self._lexical_analyzer.current_char = lookahead_character
        self._lexical_analyzer.line = lookahead_line
        self._lexical_analyzer.column = lookahead_column

        return next_token

    def _program(self) -> NodeProgram:
        return NodeProgram(self._block())

    def _block(self) -> NodeBlock:
        self._consume(TokenType.LEFT_BRACE)

        if self._current_token.type == TokenType.NEWLINE:
            self._consume(TokenType.NEWLINE)

        statements: list[NodeStatement] = []

        while self._current_token.type != TokenType.RIGHT_BRACE:
            if self._current_token.type == TokenType.NEWLINE:
                self._consume(TokenType.NEWLINE)
                continue

            statements.append(self._statement())

            if self._current_token.type == TokenType.NEWLINE:
                self._consume(TokenType.NEWLINE)
            elif self._current_token.type != TokenType.RIGHT_BRACE:
                raise SyntacticError(
                    ErrorCode.UNEXPECTED_TOKEN,
                    f"Expected NEWLINE or RIGHT_BRACE, got {self._current_token.type.value}",
                    self._current_token,
                )

        self._consume(TokenType.RIGHT_BRACE)
        return NodeBlock(statements if statements else None)

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
            case TokenType.IDENTIFIER:
                return self._assignment_statement()
            case TokenType.GIVE:
                return self._give_statement()
            case TokenType.SHOW:
                return self._show_statement()
            case TokenType.IF:
                return self._if_statement()
            case TokenType.WHILE:
                return self._while_statement()
            case TokenType.SKIP:
                return self._skip_statement()
            case TokenType.STOP:
                return self._stop_statement()
            case _:
                raise SyntacticError(
                    ErrorCode.UNEXPECTED_TOKEN,
                    f"Expected statement, got {self._current_token.type.value}",
                    self._current_token,
                )

    def _variable_declaration(self) -> NodeVariableDeclaration:
        self._consume(TokenType.LET)
        var_type: NodeType = self._type()
        identifiers: list[NodeIdentifier] = self._identifier_list()
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
        const_type: NodeType = self._type()
        identifiers: list[NodeIdentifier] = self._identifier_list()
        self._consume(TokenType.ASSIGN)
        expressions: list[NodeExpression] = self._expression_list()

        if len(identifiers) != len(expressions):
            raise SyntacticError(
                ErrorCode.WRONG_NUMBER_OF_EXPRESSIONS,
                f"Expected {len(identifiers)} expressions, got {len(expressions)}",
                self._current_token,
            )

        return NodeConstantDeclaration(const_type, identifiers, expressions)

    def _identifier_list(self) -> list[NodeIdentifier]:
        identifiers: list[NodeIdentifier] = [self._identifier()]
        while self._current_token.type == TokenType.COMMA:
            self._consume(TokenType.COMMA)
            identifiers.append(self._identifier())
        return identifiers

    def _expression_list(self) -> list[NodeExpression]:
        expressions: list[NodeExpression] = [self._expression()]
        while self._current_token.type == TokenType.COMMA:
            self._consume(TokenType.COMMA)
            expressions.append(self._expression())
        return expressions

    def _function_declaration(self) -> NodeFunctionDeclaration:
        self._consume(TokenType.FUNC)
        name: NodeIdentifier = self._identifier()
        self._consume(TokenType.LEFT_PARENTHESIS)

        parameters: Optional[list[NodeParameter]] = None
        if self._current_token.type != TokenType.RIGHT_PARENTHESIS:
            parameters = self._parameter_list()

        self._consume(TokenType.RIGHT_PARENTHESIS)
        give_type: NodeType = self._give_type()
        block: NodeBlock = self._block()
        return NodeFunctionDeclaration(name, parameters, give_type, block)

    def _procedure_declaration(self) -> NodeProcedureDeclaration:
        self._consume(TokenType.PROC)
        name: NodeIdentifier = self._identifier()
        self._consume(TokenType.LEFT_PARENTHESIS)

        parameters: Optional[list[NodeParameter]] = None
        if self._current_token.type != TokenType.RIGHT_PARENTHESIS:
            parameters = self._parameter_list()

        self._consume(TokenType.RIGHT_PARENTHESIS)
        block: NodeBlock = self._block()
        return NodeProcedureDeclaration(name, parameters, block)

    def _parameter_list(self) -> list[NodeParameter]:
        parameters: list[NodeParameter] = [self._parameter()]
        while self._current_token.type == TokenType.COMMA:
            self._consume(TokenType.COMMA)
            parameters.append(self._parameter())
        return parameters

    def _parameter(self) -> NodeParameter:
        parameter_type: NodeType = self._type()
        identifier: NodeIdentifier = self._identifier()
        return NodeParameter(identifier, parameter_type)

    def _give_type(self) -> NodeType:
        self._consume(TokenType.ARROW)
        return self._type()

    def _function_call(self) -> NodeFunctionCall:
        name: NodeIdentifier = self._identifier()
        self._consume(TokenType.LEFT_PARENTHESIS)

        arguments: Optional[list[NodeExpression]] = None
        if self._current_token.type != TokenType.RIGHT_PARENTHESIS:
            arguments = self._argument_list()

        self._consume(TokenType.RIGHT_PARENTHESIS)
        return NodeFunctionCall(name, arguments)

    def _procedure_call(self) -> NodeProcedureCall:
        self._consume(TokenType.EXEC)
        name: NodeIdentifier = self._identifier()
        self._consume(TokenType.LEFT_PARENTHESIS)

        arguments: Optional[list[NodeExpression]] = None
        if self._current_token.type != TokenType.RIGHT_PARENTHESIS:
            arguments = self._argument_list()

        self._consume(TokenType.RIGHT_PARENTHESIS)
        return NodeProcedureCall(name, arguments)

    def _argument_list(self) -> list[NodeExpression]:
        arguments: list[NodeExpression] = [self._expression()]
        while self._current_token.type == TokenType.COMMA:
            self._consume(TokenType.COMMA)
            arguments.append(self._expression())
        return arguments

    def _assignment_statement(self) -> NodeAssignmentStatement:
        identifier: NodeIdentifier = self._identifier()
        self._consume(TokenType.ASSIGN)
        expression: NodeExpression = self._expression()
        return NodeAssignmentStatement(identifier, expression)

    def _give_statement(self) -> NodeGiveStatement:
        self._consume(TokenType.GIVE)
        if self._current_token.type in (TokenType.NEWLINE, TokenType.RIGHT_BRACE):
            return NodeGiveStatement(None)
        return NodeGiveStatement(self._expression())

    def _show_statement(self) -> NodeShowStatement:
        self._consume(TokenType.SHOW)
        return NodeShowStatement(self._expression())

    def _if_statement(self) -> NodeIfStatement:
        self._consume(TokenType.IF)
        condition: NodeBooleanExpression = self._boolean_expression()
        block: NodeBlock = self._block()
        elifs: Optional[list[NodeElif]] = None
        else_: Optional[NodeElse] = None

        if self._current_token.type == TokenType.ELIF:
            elifs = self._elifs()

        if self._current_token.type == TokenType.ELSE:
            else_ = self._else()

        return NodeIfStatement(condition, block, elifs, else_)

    def _elifs(self) -> list[NodeElif]:
        elifs: list[NodeElif] = []
        while self._current_token.type == TokenType.ELIF:
            elifs.append(self._elif())
        return elifs

    def _elif(self) -> NodeElif:
        self._consume(TokenType.ELIF)
        condition: NodeBooleanExpression = self._boolean_expression()
        block: NodeBlock = self._block()
        return NodeElif(condition, block)

    def _else(self) -> NodeElse:
        self._consume(TokenType.ELSE)
        return NodeElse(self._block())

    def _while_statement(self) -> NodeWhileStatement:
        self._consume(TokenType.WHILE)
        condition: NodeBooleanExpression = self._boolean_expression()
        block: NodeBlock = self._block()
        return NodeWhileStatement(condition, block)

    def _skip_statement(self) -> NodeSkipStatement:
        self._consume(TokenType.SKIP)
        return NodeSkipStatement()

    def _stop_statement(self) -> NodeStopStatement:
        self._consume(TokenType.STOP)
        return NodeStopStatement()

    def _type(self) -> NodeType:
        token: Token = self._current_token
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
        token: Token = self._consume(TokenType.IDENTIFIER)
        return NodeIdentifier(token.value)

    def _expression(self) -> NodeExpression:
        return self._boolean_expression()

    def _boolean_expression(self) -> NodeBooleanExpression:
        return self._logical_or_expression()

    def _logical_or_expression(self) -> NodeBooleanExpression:
        left: NodeBooleanExpression = self._logical_and_expression()

        while self._current_token.type == TokenType.OR:
            operator: Token = self._current_token
            self._consume(TokenType.OR)
            right: NodeBooleanExpression = self._logical_and_expression()
            left = NodeBinaryBooleanOperation(left, operator.value, right)

        return left

    def _logical_and_expression(self) -> NodeBooleanExpression:
        left: NodeBooleanExpression = self._logical_not_expression()

        while self._current_token.type == TokenType.AND:
            operator: Token = self._current_token
            self._consume(TokenType.AND)
            right: NodeBooleanExpression = self._logical_not_expression()
            left = NodeBinaryBooleanOperation(left, operator.value, right)

        return left

    def _logical_not_expression(self) -> NodeBooleanExpression:
        if self._current_token.type == TokenType.NOT:
            operator: Token = self._current_token
            self._consume(TokenType.NOT)
            operand: NodeBooleanExpression = self._primary_boolean_expression()
            return NodeUnaryBooleanOperation(operator.value, operand)

        return self._primary_boolean_expression()

    def _primary_boolean_expression(self) -> NodeBooleanExpression:
        if self._current_token.type == TokenType.BOOL_LITERAL:
            token: Token = self._consume(TokenType.BOOL_LITERAL)
            return NodeBooleanLiteral(token.value)

        if self._current_token.type == TokenType.LEFT_PARENTHESIS:
            self._consume(TokenType.LEFT_PARENTHESIS)
            boolean_expression: NodeBooleanExpression = self._boolean_expression()
            self._consume(TokenType.RIGHT_PARENTHESIS)
            return boolean_expression

        return self._comparison_expression()

    def _comparison_expression(self) -> NodeBooleanExpression:
        left: NodeArithmeticExpression = self._arithmetic_expression()

        comparison_operators: set[TokenType] = {
            TokenType.EQUAL,
            TokenType.NOT_EQUAL,
            TokenType.LESS,
            TokenType.GREATER,
            TokenType.LESS_EQUAL,
            TokenType.GREATER_EQUAL,
        }

        if self._current_token.type in comparison_operators:
            operator: Token = self._current_token
            self._consume(operator.type)
            right: NodeArithmeticExpression = self._arithmetic_expression()
            return NodeComparison(left, operator.value, right)

        return NodeArithmeticExpressionAsBoolean(left)

    def _arithmetic_expression(self) -> NodeArithmeticExpression:
        return self._additive_expression()

    def _additive_expression(self) -> NodeArithmeticExpression:
        left: NodeArithmeticExpression = self._multiplicative_expression()
        while self._current_token.type in {TokenType.PLUS, TokenType.MINUS}:
            operator: Token = self._current_token
            self._consume(operator.type)
            right: NodeArithmeticExpression = self._multiplicative_expression()
            left = NodeBinaryArithmeticOperation(left, operator.value, right)
        return left

    def _multiplicative_expression(self) -> NodeArithmeticExpression:
        left: NodeArithmeticExpression = self._power_expression()
        while self._current_token.type in {
            TokenType.MULTIPLY,
            TokenType.DIVIDE,
            TokenType.FLOOR_DIVIDE,
            TokenType.MODULO,
        }:
            operator: Token = self._current_token
            self._consume(operator.type)
            right: NodeArithmeticExpression = self._power_expression()
            left = NodeBinaryArithmeticOperation(left, operator.value, right)
        return left

    def _power_expression(self) -> NodeArithmeticExpression:
        left: NodeArithmeticExpression = self._unary_expression()
        if self._current_token.type == TokenType.POWER:
            operator: Token = self._current_token
            self._consume(TokenType.POWER)
            right: NodeArithmeticExpression = self._power_expression()
            return NodeBinaryArithmeticOperation(left, operator.value, right)
        return left

    def _unary_expression(self) -> NodeArithmeticExpression:
        if self._current_token.type in {TokenType.PLUS, TokenType.MINUS}:
            operator: Token = self._current_token
            self._consume(operator.type)
            operand: NodeArithmeticExpression = self._unary_expression()
            return NodeUnaryArithmeticOperation(operator.value, operand)
        return self._primary_expression()

    def _primary_expression(self) -> NodeArithmeticExpression:
        token: Token = self._current_token

        if token.type == TokenType.INT_LITERAL:
            self._consume(TokenType.INT_LITERAL)
            return NodeIntegerLiteral(token.value)

        if token.type == TokenType.FLOAT_LITERAL:
            self._consume(TokenType.FLOAT_LITERAL)
            return NodeFloatLiteral(token.value)

        if token.type == TokenType.STRING_LITERAL:
            self._consume(TokenType.STRING_LITERAL)
            return NodeStringLiteral(token.value)

        if token.type == TokenType.IDENTIFIER:
            lookahead_position: int = self._lexical_analyzer.position
            lookahead_character: Optional[str] = self._lexical_analyzer.current_char
            lookahead_line: int = self._lexical_analyzer.line
            lookahead_column: int = self._lexical_analyzer.column

            try:
                self._consume(TokenType.IDENTIFIER)
                if self._current_token.type == TokenType.LEFT_PARENTHESIS:
                    self._lexical_analyzer.position = lookahead_position
                    self._lexical_analyzer.current_char = lookahead_character
                    self._lexical_analyzer.line = lookahead_line
                    self._lexical_analyzer.column = lookahead_column
                    self._current_token = token
                    return self._function_call()
                else:
                    return NodeIdentifier(token.value)
            except Exception:
                self._lexical_analyzer.position = lookahead_position
                self._lexical_analyzer.current_char = lookahead_character
                self._lexical_analyzer.line = lookahead_line
                self._lexical_analyzer.column = lookahead_column
                self._current_token = token
                raise

        if token.type == TokenType.LEFT_PARENTHESIS:
            self._consume(TokenType.LEFT_PARENTHESIS)
            arithmetic_expression: NodeArithmeticExpression = (
                self._arithmetic_expression()
            )
            self._consume(TokenType.RIGHT_PARENTHESIS)
            return arithmetic_expression

        raise SyntacticError(
            ErrorCode.UNEXPECTED_TOKEN,
            f"Expected arithmetic expression, got {token.type.value}",
            token,
        )
