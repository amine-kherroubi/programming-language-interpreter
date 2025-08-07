from typing import Optional
from lexical_analysis.lexical_analyzer import LexicalAnalyzer
from lexical_analysis.tokens import Token, TokenType
from syntactic_analysis.ast import (
    NodeAST,
    NodeBlock,
    NodeConstantDeclaration,
    NodeExpression,
    NodeGiveStatement,
    NodeIdentifier,
    NodeNumericLiteral,
    NodeParameter,
    NodeProgram,
    NodeSameTypeConstantDeclarationGroup,
    NodeSameTypeVariableDeclarationGroup,
    NodeStatement,
    NodeType,
    NodeUnit,
    NodeUnitUse,
    NodeAssignmentStatement,
    NodeBinaryOperation,
    NodeUnaryOperation,
    NodeVariableDeclaration,
)
from utils.error_handling import SyntacticError, ErrorCode


class SyntacticAnalyzer(object):
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
        block: NodeBlock = self._block()
        return NodeProgram(block)

    def _block(self) -> NodeBlock:
        self._consume(TokenType.LEFT_BRACE)
        statements: list[NodeStatement] = []
        if self._current_token.type != TokenType.RIGHT_BRACE:
            statements.append(self._statement())
            while self._current_token.type == TokenType.NEWLINE:
                self._consume(TokenType.NEWLINE)
                if self._current_token.type == TokenType.RIGHT_BRACE:
                    break
                statements.append(self._statement())
        self._consume(TokenType.RIGHT_BRACE)
        return NodeBlock(statements)

    def _identifier(self) -> NodeIdentifier:
        token: Token = self._current_token
        self._consume(TokenType.IDENTIFIER)
        return NodeIdentifier(token.value)

    def _statement(
        self,
    ) -> NodeStatement:
        if (
            self._current_token.type == TokenType.IDENTIFIER
            and self._lexical_analyzer.current_char == "("
        ):
            return self._unit_use()
        if self._current_token.type == TokenType.IDENTIFIER:
            return self._assignment()
        if self._current_token.type == TokenType.LET:
            return self._variable_declaration()
        if self._current_token.type == TokenType.KEEP:
            return self._constant_declaration()
        if self._current_token.type == TokenType.GIVE:
            return self._give_statement()
        raise SyntacticError(
            ErrorCode.UNEXPECTED_TOKEN, "Expected a statement", self._current_token
        )

    def _parameter(self) -> NodeParameter:
        parameter_identifier: NodeIdentifier = self._identifier()
        self._consume(TokenType.COLON)
        parameter_type: NodeType = self._type()
        return NodeParameter(parameter_identifier, parameter_type)

    def _parameters(self) -> list[NodeParameter]:
        parameters: list[NodeParameter] = [self._parameter()]
        while self._current_token.type == TokenType.COMMA:
            self._consume(TokenType.COMMA)
            parameters.append(self._parameter())
        return parameters

    def _variable_declaration(self) -> NodeVariableDeclaration:
        self._consume(TokenType.LET)
        same_type_groups: list[NodeSameTypeVariableDeclarationGroup] = [
            self._same_type_variable_declaration_group()
        ]
        while self._current_token.type == TokenType.SEMICOLON:
            self._consume(TokenType.SEMICOLON)
            same_type_groups.append(self._same_type_variable_declaration_group())
        return NodeVariableDeclaration(same_type_groups)

    def _same_type_variable_declaration_group(
        self,
    ) -> NodeSameTypeVariableDeclarationGroup:
        token: Token = self._current_token
        identifier_group: list[NodeIdentifier] = [self._identifier()]
        while self._current_token.type == TokenType.COMMA:
            self._consume(TokenType.COMMA)
            identifier_group.append(self._identifier())
        self._consume(TokenType.COLON)
        type: NodeType = self._type()
        if self._current_token.type == TokenType.ASSIGN:
            self._consume(TokenType.ASSIGN)
            expression_group: list[NodeExpression] = [self._expression()]
            while self._current_token.type == TokenType.COMMA:
                self._consume(TokenType.COMMA)
                expression_group.append(self._expression())
            if (x := len(identifier_group)) != (y := len(expression_group)):
                raise SyntacticError(
                    ErrorCode.WRONG_NUMBER_OF_EXPRESSIONS,
                    f"Expected {x} assignable expressions, got {y}",
                    token,
                )
            return NodeSameTypeVariableDeclarationGroup(
                identifier_group, type, expression_group
            )
        return NodeSameTypeVariableDeclarationGroup(identifier_group, type, None)

    def _constant_declaration(self) -> NodeConstantDeclaration:
        self._consume(TokenType.KEEP)
        same_type_groups: list[NodeSameTypeConstantDeclarationGroup] = [
            self._same_type_constant_declaration_group()
        ]
        while self._current_token.type == TokenType.SEMICOLON:
            self._consume(TokenType.SEMICOLON)
            same_type_groups.append(self._same_type_constant_declaration_group())
        return NodeConstantDeclaration(same_type_groups)

    def _same_type_constant_declaration_group(
        self,
    ) -> NodeSameTypeConstantDeclarationGroup:
        token: Token = self._current_token
        identifier_group: list[NodeIdentifier] = [self._identifier()]
        while self._current_token.type == TokenType.COMMA:
            self._consume(TokenType.COMMA)
            identifier_group.append(self._identifier())
        self._consume(TokenType.COLON)
        type: NodeType = self._type()
        if self._current_token.type == TokenType.ASSIGN:
            self._consume(TokenType.ASSIGN)
            expression_group: list[NodeExpression] = [self._expression()]
            while self._current_token.type == TokenType.COMMA:
                self._consume(TokenType.COMMA)
                expression_group.append(self._expression())
            if (x := len(identifier_group)) != (y := len(expression_group)):
                raise SyntacticError(
                    ErrorCode.WRONG_NUMBER_OF_EXPRESSIONS,
                    f"Expected {x} assignable expressions, got {y}",
                    token,
                )
            return NodeSameTypeConstantDeclarationGroup(
                identifier_group, type, expression_group
            )
        raise SyntacticError(
            ErrorCode.UNINITIALIZED_CONSTANT, "Expected initial value", token
        )

    def _give_statement(self) -> NodeGiveStatement:
        self._consume(TokenType.GIVE)
        if self._current_token.type in (TokenType.RIGHT_BRACE, TokenType.NEWLINE):
            return NodeGiveStatement(None)
        return NodeGiveStatement(self._expression())

    def _type(self) -> NodeType:
        token: Token = self._current_token
        if token.type == TokenType.WHOLE_TYPE:
            self._consume(TokenType.WHOLE_TYPE)
            return NodeType(token)
        elif token.type == TokenType.REAL_TYPE:
            self._consume(TokenType.REAL_TYPE)
            return NodeType(token)
        elif token.type == TokenType.TEXT_TYPE:
            self._consume(TokenType.TEXT_TYPE)
            return NodeType(token)
        elif token.type == TokenType.TRUTH_TYPE:
            self._consume(TokenType.TRUTH_TYPE)
            return NodeType(token)
        elif token.type == TokenType.UNIT_TYPE:
            self._consume(TokenType.UNIT_TYPE)
            return NodeType(token)
        else:
            raise SyntacticError(ErrorCode.UNEXPECTED_TOKEN, "Expected type", token)

    def _assignment(self) -> NodeAssignmentStatement:
        identifier: NodeIdentifier = self._identifier()
        self._consume(TokenType.ASSIGN)
        return NodeAssignmentStatement(identifier, self._expression())

    def _factor(self) -> NodeExpression:
        token: Token = self._current_token
        if (
            token.type == TokenType.IDENTIFIER
            and self._lexical_analyzer.current_char == "("
        ):
            return self._unit_use()
        elif token.type == TokenType.IDENTIFIER:
            return self._identifier()
        elif self._current_token.type == TokenType.LEFT_BRACE:
            return self._unit()
        elif token.type == TokenType.WHOLE_LITERAL:
            self._consume(TokenType.WHOLE_LITERAL)
            return NodeNumericLiteral(token.value)
        elif token.type == TokenType.REAL_LITERAL:
            self._consume(TokenType.REAL_LITERAL)
            return NodeNumericLiteral(token.value)
        elif token.type == TokenType.LEFT_PARENTHESIS:
            self._consume(TokenType.LEFT_PARENTHESIS)
            node: NodeExpression = self._expression()
            self._consume(TokenType.RIGHT_PARENTHESIS)
            return node
        elif token.type in (TokenType.PLUS, TokenType.MINUS):
            self._consume(token.type)
            operand: NodeExpression = self._factor()
            return NodeUnaryOperation(token.value, operand)
        else:
            raise SyntacticError(
                ErrorCode.UNEXPECTED_TOKEN,
                "Expected number, unary operator, or '('",
                token,
            )

    def _term(self) -> NodeExpression:
        node: NodeExpression = self._factor()
        while self._current_token.type in (
            TokenType.MULTIPLY,
            TokenType.DIVIDE,
            TokenType.FLOOR_DIVIDE,
            TokenType.MODULO,
        ):
            token: Token = self._current_token
            self._consume(token.type)
            right: NodeExpression = self._factor()
            node = NodeBinaryOperation(node, token.value, right)
        return node

    def _power_expression(self) -> NodeExpression:
        node: NodeExpression = self._term()
        if self._current_token.type == TokenType.POWER:
            token: Token = self._current_token
            self._consume(TokenType.POWER)
            right: NodeExpression = self._power_expression()
            node = NodeBinaryOperation(node, token.value, right)
        return node

    def _expression(self) -> NodeExpression:
        node: NodeExpression = self._power_expression()
        while self._current_token.type in (TokenType.PLUS, TokenType.MINUS):
            token: Token = self._current_token
            self._consume(token.type)
            right: NodeExpression = self._power_expression()
            node = NodeBinaryOperation(node, token.value, right)
        return node

    def _unit(self) -> NodeUnit:
        parameters: Optional[list[NodeParameter]] = None
        type: Optional[NodeType] = None
        if self._current_token.type == TokenType.LEFT_BRACKET:
            self._consume(TokenType.LEFT_BRACKET)
            if self._current_token.type != TokenType.RIGHT_BRACKET:
                parameters = self._parameters()
            self._consume(TokenType.RIGHT_BRACKET)
            if self._current_token.type == TokenType.ARROW:
                self._consume(TokenType.ARROW)
                type = self._type()
        return NodeUnit(parameters, type, self._block())

    def _unit_use(self) -> NodeUnitUse:
        unit_identifier: str = self._identifier().name
        arguments: Optional[list[NodeExpression]] = None
        self._consume(TokenType.LEFT_PARENTHESIS)
        if self._current_token.type != TokenType.RIGHT_PARENTHESIS:
            arguments = self._arguments()
        self._consume(TokenType.RIGHT_PARENTHESIS)
        return NodeUnitUse(unit_identifier, arguments)

    def _arguments(self) -> list[NodeExpression]:
        arguments: list[NodeExpression] = [self._expression()]
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
