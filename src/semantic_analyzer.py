from .symbol_table import SymbolTable


class SemanticAnalyzer:
    def __init__(self, error_handler=None):
        self.symbol_table = SymbolTable()
        self.error_handler = error_handler
        self.current_function = None

    def analyze(self, ast):
        return ast.accept(self)

    def visit_program(self, node):
        for statement in node.statements:
            statement.accept(self)

    def visit_declaration(self, node):
        var_type = node.var_type
        var_name = node.identifier.name
        success, error = self.symbol_table.declare(
            var_name, var_type, node.identifier.line, node.identifier.column
        )
        if not success and self.error_handler:
            self.error_handler.add_semantic_error(error, node.identifier.line, node.identifier.column)

    def visit_assignment(self, node):
        var_name = node.identifier.name
        if not self.symbol_table.is_declared(var_name):
            if self.error_handler:
                self.error_handler.add_semantic_error(
                    f"Assignment to undeclared variable: {var_name}",
                    node.identifier.line, node.identifier.column
                )
        expr_type = node.expression.accept(self)
        if self.symbol_table.is_declared(var_name):
            decl_type = self.symbol_table.get_type(var_name)
            if decl_type and expr_type and decl_type != expr_type:
                if self.error_handler:
                    self.error_handler.add_semantic_error(
                        f"Type mismatch: cannot assign {expr_type} to {decl_type}",
                        node.identifier.line, node.identifier.column
                    )

    def visit_if_statement(self, node):
        node.condition.accept(self)
        self.symbol_table.enter_scope()
        for stmt in node.then_block:
            stmt.accept(self)
        self.symbol_table.exit_scope()
        if node.else_block:
            self.symbol_table.enter_scope()
            for stmt in node.else_block:
                stmt.accept(self)
            self.symbol_table.exit_scope()

    def visit_while_statement(self, node):
        node.condition.accept(self)
        self.symbol_table.enter_scope()
        for stmt in node.body:
            stmt.accept(self)
        self.symbol_table.exit_scope()

    def visit_binary_expression(self, node):
        left_type = node.left.accept(self)
        right_type = node.right.accept(self)
        op = node.operator
        if op == '+':
            if left_type == 'string' and right_type == 'string':
                return 'string'
            if left_type == 'string' or right_type == 'string':
                if self.error_handler:
                    self.error_handler.add_semantic_error(
                        f"Cannot add {left_type} and {right_type}",
                        node.line, node.column
                    )
                return 'error'
            return 'int'
        elif op in ('-', '*', '/'):
            if left_type == 'string' or right_type == 'string':
                if self.error_handler:
                    self.error_handler.add_semantic_error(
                        f"Cannot perform arithmetic ({op}) on strings",
                        node.line, node.column
                    )
                return 'error'
            return 'int'
        elif op in ('>', '<', '='):
            return 'int'
        return 'unknown'

    def visit_identifier(self, node):
        if not self.symbol_table.is_declared(node.name):
            if self.error_handler:
                self.error_handler.add_semantic_error(
                    f"Use of undeclared variable: {node.name}",
                    node.line, node.column
                )
            return 'unknown'
        return self.symbol_table.get_type(node.name)

    def visit_number_literal(self, node):
        return 'int'

    def visit_string_literal(self, node):
        return 'string'

    def visit_unary_expression(self, node):
        return node.operand.accept(self)

    def visit_empty_statement(self, node):
        pass