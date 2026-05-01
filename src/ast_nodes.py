class ASTNode:
    def __init__(self, line=0, column=0):
        self.line = line
        self.column = column

    def accept(self, visitor):
        raise NotImplementedError()


class Program(ASTNode):
    def __init__(self, statements, line=0, column=0):
        super().__init__(line, column)
        self.statements = statements

    def accept(self, visitor):
        return visitor.visit_program(self)


class Declaration(ASTNode):
    def __init__(self, var_type, identifier, line=0, column=0):
        super().__init__(line, column)
        self.var_type = var_type
        self.identifier = identifier

    def accept(self, visitor):
        return visitor.visit_declaration(self)


class Assignment(ASTNode):
    def __init__(self, identifier, expression, line=0, column=0):
        super().__init__(line, column)
        self.identifier = identifier
        self.expression = expression

    def accept(self, visitor):
        return visitor.visit_assignment(self)


class IfStatement(ASTNode):
    def __init__(self, condition, then_block, else_block=None, line=0, column=0):
        super().__init__(line, column)
        self.condition = condition
        self.then_block = then_block
        self.else_block = else_block

    def accept(self, visitor):
        return visitor.visit_if_statement(self)


class WhileStatement(ASTNode):
    def __init__(self, condition, body, line=0, column=0):
        super().__init__(line, column)
        self.condition = condition
        self.body = body

    def accept(self, visitor):
        return visitor.visit_while_statement(self)


class BinaryExpression(ASTNode):
    def __init__(self, left, operator, right, line=0, column=0):
        super().__init__(line, column)
        self.left = left
        self.operator = operator
        self.right = right

    def accept(self, visitor):
        return visitor.visit_binary_expression(self)


class Identifier(ASTNode):
    def __init__(self, name, line=0, column=0):
        super().__init__(line, column)
        self.name = name

    def accept(self, visitor):
        return visitor.visit_identifier(self)


class NumberLiteral(ASTNode):
    def __init__(self, value, line=0, column=0):
        super().__init__(line, column)
        self.value = int(value)

    def accept(self, visitor):
        return visitor.visit_number_literal(self)


class StringLiteral(ASTNode):
    def __init__(self, value, line=0, column=0):
        super().__init__(line, column)
        self.value = value[1:-1] if value.startswith('"') else value

    def accept(self, visitor):
        return visitor.visit_string_literal(self)


class UnaryExpression(ASTNode):
    def __init__(self, operator, operand, line=0, column=0):
        super().__init__(line, column)
        self.operator = operator
        self.operand = operand

    def accept(self, visitor):
        return visitor.visit_unary_expression(self)


class EmptyStatement(ASTNode):
    def accept(self, visitor):
        return visitor.visit_empty_statement(self)