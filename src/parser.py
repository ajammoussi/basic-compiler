from .lexer import TokenType, Token
from .ast_nodes import (
    Program, Declaration, Assignment, IfStatement, WhileStatement,
    BinaryExpression, Identifier, NumberLiteral, StringLiteral,
    UnaryExpression, EmptyStatement
)
from .error_handler import ParserError


class Parser:
    def __init__(self, tokens, error_handler=None):
        self.tokens = tokens
        self.pos = 0
        self.error_handler = error_handler

    def current_token(self):
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return None

    def peek_token(self, offset=1):
        idx = self.pos + offset
        if idx < len(self.tokens):
            return self.tokens[idx]
        return None

    def advance(self):
        token = self.current_token()
        self.pos += 1
        return token

    def expect(self, token_type):
        token = self.current_token()
        if token is None or token.type != token_type:
            if self.error_handler:
                expected_name = token_type.name if isinstance(token_type, TokenType) else str(token_type)
                actual = token.type.name if token else "EOF"
                self.error_handler.add_parser_error(
                    f"Expected {expected_name}, got {actual}",
                    token.line if token else None,
                    token.column if token else None
                )
            return None
        return self.advance()

    def match(self, token_type):
        if self.current_token() and self.current_token().type == token_type:
            return self.advance()
        return None

    def parse(self):
        program = self.parse_program()
        if self.current_token() and self.current_token().type != TokenType.EOF:
            if self.error_handler:
                self.error_handler.add_parser_error(
                    f"Unexpected token: {self.current_token().type.name}",
                    self.current_token().line,
                    self.current_token().column
                )
        return program

    def parse_program(self):
        statements = []
        while self.current_token() and self.current_token().type != TokenType.EOF:
            stmt = self.parse_statement()
            if stmt:
                statements.append(stmt)
        return Program(statements)

    def parse_statement(self):
        token = self.current_token()
        if token is None:
            return None

        if token.type == TokenType.KW_INT or token.type == TokenType.KW_STRING:
            return self.parse_declaration()
        elif token.type == TokenType.KW_IF:
            return self.parse_if_statement()
        elif token.type == TokenType.KW_WHILE:
            return self.parse_while_statement()
        elif token.type == TokenType.IDENTIFIER:
            return self.parse_assignment()
        elif token.type == TokenType.LBRACE:
            return self.parse_block()
        else:
            self.error_handler.add_parser_error(
                f"Unexpected token: {token.type.name}",
                token.line, token.column
            )
            self.advance()
            return None

    def parse_declaration(self):
        token = self.advance()
        var_type = token.value
        line, column = token.line, token.column
        ident_token = self.expect(TokenType.IDENTIFIER)
        if ident_token is None:
            return None
        self.expect(TokenType.SEMICOLON)
        return Declaration(
            var_type,
            Identifier(ident_token.value, ident_token.line, ident_token.column),
            line, column
        )

    def parse_assignment(self):
        ident_token = self.expect(TokenType.IDENTIFIER)
        if ident_token is None:
            return None
        line, column = ident_token.line, ident_token.column
        self.expect(TokenType.EQUALS)
        expr = self.parse_expression()
        if expr is None:
            return None
        self.expect(TokenType.SEMICOLON)
        return Assignment(
            Identifier(ident_token.value, ident_token.line, ident_token.column),
            expr, line, column
        )

    def parse_if_statement(self):
        if_token = self.current_token()
        self.expect(TokenType.KW_IF)
        condition = self.parse_expression()
        if condition is None:
            return None
        self.expect(TokenType.KW_THEN)
        if self.current_token() and self.current_token().type == TokenType.LBRACE:
            self.expect(TokenType.LBRACE)
            then_block = self.parse_statement_list()
            self.expect(TokenType.RBRACE)
        else:
            stmt = self.parse_statement()
            then_block = [stmt] if stmt else []
        else_block = None
        if self.match(TokenType.KW_ELSE):
            if self.current_token() and self.current_token().type == TokenType.LBRACE:
                self.expect(TokenType.LBRACE)
                else_block = self.parse_statement_list()
                self.expect(TokenType.RBRACE)
            else:
                stmt = self.parse_statement()
                else_block = [stmt] if stmt else []
        return IfStatement(condition, then_block, else_block, if_token.line, if_token.column)

    def parse_while_statement(self):
        while_token = self.current_token()
        self.expect(TokenType.KW_WHILE)
        condition = self.parse_expression()
        if condition is None:
            return None
        self.expect(TokenType.LBRACE)
        body = self.parse_statement_list()
        self.expect(TokenType.RBRACE)
        return WhileStatement(condition, body, while_token.line, while_token.column)

    def parse_block(self):
        lbrace = self.current_token()
        self.expect(TokenType.LBRACE)
        statements = self.parse_statement_list()
        self.expect(TokenType.RBRACE)
        return Program(statements, lbrace.line, lbrace.column) if statements else EmptyStatement()

    def parse_statement_list(self):
        statements = []
        while self.current_token() and self.current_token().type not in (
            TokenType.EOF, TokenType.RBRACE, TokenType.KW_ELSE
        ):
            stmt = self.parse_statement()
            if stmt:
                statements.append(stmt)
        return statements

    def parse_expression(self):
        return self.parse_comparison()

    def parse_comparison(self):
        left = self.parse_addition()
        while self.current_token() and self.current_token().type in (
            TokenType.GREATER, TokenType.LESS, TokenType.EQUALS
        ):
            op_token = self.advance()
            right = self.parse_addition()
            left = BinaryExpression(left, op_token.value, right, left.line, left.column)
        return left

    def parse_addition(self):
        left = self.parse_multiplication()
        while self.current_token() and self.current_token().type in (
            TokenType.PLUS, TokenType.MINUS
        ):
            op_token = self.advance()
            right = self.parse_multiplication()
            left = BinaryExpression(left, op_token.value, right, left.line, left.column)
        return left

    def parse_multiplication(self):
        left = self.parse_unary()
        while self.current_token() and self.current_token().type in (
            TokenType.MULTIPLY, TokenType.DIVIDE
        ):
            op_token = self.advance()
            right = self.parse_unary()
            left = BinaryExpression(left, op_token.value, right, left.line, left.column)
        return left

    def parse_unary(self):
        if self.current_token() and self.current_token().type == TokenType.MINUS:
            op_token = self.advance()
            operand = self.parse_unary()
            return UnaryExpression('-', operand, op_token.line, op_token.column)
        return self.parse_primary()

    def parse_primary(self):
        token = self.current_token()
        if token is None:
            return None

        if token.type == TokenType.IDENTIFIER:
            self.advance()
            return Identifier(token.value, token.line, token.column)
        elif token.type == TokenType.NUMBER:
            self.advance()
            return NumberLiteral(token.value, token.line, token.column)
        elif token.type == TokenType.STRING_LITERAL:
            self.advance()
            return StringLiteral(token.value, token.line, token.column)
        elif token.type == TokenType.LPAREN:
            lparen = self.advance()
            expr = self.parse_expression()
            self.expect(TokenType.RPAREN)
            return expr
        else:
            self.error_handler.add_parser_error(
                f"Unexpected token in expression: {token.type.name}",
                token.line, token.column
            )
            self.advance()
            return None


def parse(tokens, error_handler=None):
    parser = Parser(tokens, error_handler)
    return parser.parse()