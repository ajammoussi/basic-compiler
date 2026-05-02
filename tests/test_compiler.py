import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.lexer import tokenize, TokenType
from src.parser import parse
from src.semantic_analyzer import SemanticAnalyzer
from src.compiler import compile_source
from src.error_handler import ErrorHandler


class TestLexer:
    def test_simple_assignment(self):
        code = 'x = 5;'
        tokens = tokenize(code)
        assert len(tokens) == 5
        assert tokens[0].type == TokenType.IDENTIFIER
        assert tokens[0].value == 'x'
        assert tokens[1].type == TokenType.EQUALS
        assert tokens[2].type == TokenType.NUMBER
        assert tokens[2].value == '5'
        assert tokens[3].type == TokenType.SEMICOLON
        assert tokens[4].type == TokenType.EOF

    def test_arithmetic_expression(self):
        code = 'z = x + (y - 3);'
        tokens = tokenize(code)
        assert tokens[0].type == TokenType.IDENTIFIER
        assert tokens[2].type == TokenType.IDENTIFIER
        assert tokens[3].type == TokenType.PLUS
        assert tokens[4].type == TokenType.LPAREN

    def test_keywords(self):
        code = 'if x then { y = 1; } else { y = 2; }'
        tokens = tokenize(code)
        token_types = [t.type for t in tokens[:-1]]
        assert TokenType.KW_IF in token_types
        assert TokenType.KW_THEN in token_types
        assert TokenType.KW_ELSE in token_types

    def test_string_literal(self):
        code = 'string name = "hello";'
        tokens = tokenize(code)
        assert tokens[3].type == TokenType.STRING_LITERAL
        assert tokens[3].value == '"hello"'

    def test_declaration(self):
        code = 'int x; string name;'
        tokens = tokenize(code)
        token_types = [t.type for t in tokens[:-1]]
        assert TokenType.KW_INT in token_types
        assert TokenType.KW_STRING in token_types

    def test_complex_expression(self):
        code = 'x = a * (b + c) - d / 2;'
        tokens = tokenize(code)
        token_types = [t.type for t in tokens[:-1]]
        assert TokenType.MULTIPLY in token_types
        assert TokenType.PLUS in token_types
        assert TokenType.MINUS in token_types
        assert TokenType.DIVIDE in token_types

    def test_pdf_example1_output_format(self):
        code = 'x = 5 + 2;'
        tokens = tokenize(code)
        result = [str(t) for t in tokens[:-1]]
        expected = ["ID('x')", "'='", 'NUM(5)', "'+'", 'NUM(2)', "';'"]
        assert result == expected, f"Expected {expected}, got {result}"

    def test_pdf_example2_output_format(self):
        code = 'z = x * (y - 3);'
        tokens = tokenize(code)
        result = [str(t) for t in tokens[:-1]]
        expected = ["ID('z')", "'='", "ID('x')", "'*'", "'('", "ID('y')", "'-'", 'NUM(3)', "')'", "';'"]
        assert result == expected, f"Expected {expected}, got {result}"

    def test_pdf_example3_output_format(self):
        code = 'if a = b then a = a + 1; else b = b - 1;'
        tokens = tokenize(code)
        result = [str(t) for t in tokens[:-1]]
        expected = ["KW('if')", "ID('a')", "'='", "ID('b')", "KW('then')",
                    "ID('a')", "'='", "ID('a')", "'+'", 'NUM(1)', "';'",
                    "KW('else')", "ID('b')", "'='", "ID('b')", "'-'", 'NUM(1)', "';'"]
        assert result == expected, f"Expected {expected}, got {result}"


class TestParser:
    def test_simple_declaration(self):
        code = 'int x;'
        tokens = tokenize(code)
        ast = parse(tokens)
        assert ast.statements[0].var_type == 'int'
        assert ast.statements[0].identifier.name == 'x'

    def test_assignment(self):
        code = 'x = 5 + 2;'
        tokens = tokenize(code)
        ast = parse(tokens)
        assert ast.statements[0].identifier.name == 'x'
        assert ast.statements[0].expression.operator == '+'

    def test_if_statement_with_braces(self):
        code = 'if x > 3 then { y = 1; }'
        tokens = tokenize(code)
        ast = parse(tokens)
        stmt = ast.statements[0]
        assert stmt.condition.operator == '>'

    def test_if_statement_without_braces(self):
        code = 'if a > b then a = a + 1;'
        tokens = tokenize(code)
        ast = parse(tokens)
        stmt = ast.statements[0]
        assert stmt.condition.operator == '>'
        assert len(stmt.then_block) == 1

    def test_if_else_with_braces(self):
        code = 'if x > 3 then { y = 1; } else { y = 2; }'
        tokens = tokenize(code)
        ast = parse(tokens)
        stmt = ast.statements[0]
        assert stmt.else_block is not None

    def test_if_else_without_braces(self):
        code = 'if a = b then a = a + 1; else b = b - 1;'
        tokens = tokenize(code)
        ast = parse(tokens)
        stmt = ast.statements[0]
        assert stmt.else_block is not None
        assert len(stmt.then_block) == 1
        assert len(stmt.else_block) == 1

    def test_nested_expressions(self):
        code = 'x = a * (b + c) - d / 2;'
        tokens = tokenize(code)
        ast = parse(tokens)
        expr = ast.statements[0].expression
        assert expr.operator == '-'

    def test_declaration_and_assignment(self):
        code = 'int x; x = 5;'
        tokens = tokenize(code)
        ast = parse(tokens)
        assert len(ast.statements) == 2
        assert ast.statements[0].var_type == 'int'
        assert ast.statements[1].identifier.name == 'x'

    def test_string_declaration(self):
        code = 'string name;'
        tokens = tokenize(code)
        ast = parse(tokens)
        assert ast.statements[0].var_type == 'string'
        assert ast.statements[0].identifier.name == 'name'

    def test_control_structure_from_pdf(self):
        code = 'if x > 10 then { x = x - 1; }'
        tokens = tokenize(code)
        ast = parse(tokens)
        stmt = ast.statements[0]
        assert type(stmt).__name__ == 'IfStatement'
        assert stmt.condition.operator == '>'

    def test_while_statement(self):
        code = 'while x > 0 { x = x - 1; }'
        tokens = tokenize(code)
        ast = parse(tokens)
        stmt = ast.statements[0]
        assert type(stmt).__name__ == 'WhileStatement'
        assert stmt.condition.operator == '>'
        assert len(stmt.body) == 1


class TestSemanticAnalyzer:
    def test_undeclared_variable_error(self):
        code = 'x = 5;'
        ast, errors = compile_source(code)
        assert len(errors) == 1
        assert 'undeclared' in str(errors[0]).lower()

    def test_type_mismatch_int_string(self):
        code = 'int x;\nstring y;\ny = x;'
        ast, errors = compile_source(code)
        assert len(errors) == 1
        assert 'type mismatch' in str(errors[0]).lower()

    def test_assigning_string_to_int(self):
        code = 'int x;\nx = "hello";'
        ast, errors = compile_source(code)
        assert len(errors) == 1
        assert 'type mismatch' in str(errors[0]).lower()

    def test_valid_int_assignment(self):
        code = 'int x;\nx = 5 + 3;'
        ast, errors = compile_source(code)
        assert len(errors) == 0

    def test_valid_string_assignment(self):
        code = 'string name;\nname = "hello";'
        ast, errors = compile_source(code)
        assert len(errors) == 0

    def test_string_concatenation_allowed(self):
        code = 'string s;\ns = "hello" + " world!";'
        ast, errors = compile_source(code)
        assert len(errors) == 0

    def test_cannot_add_int_and_string(self):
        code = 'int x;\nstring s;\ns = x + "hello";'
        ast, errors = compile_source(code)
        assert len(errors) >= 1

    def test_valid_if_statement(self):
        code = 'int a;\nint x;\na = 5;\nif a > 3 then { x = 1; }'
        ast, errors = compile_source(code)
        assert len(errors) == 0

    def test_duplicate_declaration_error(self):
        code = 'int x;\nint x;'
        ast, errors = compile_source(code)
        assert len(errors) == 1
        assert 'already declared' in str(errors[0]).lower()

    def test_undeclared_in_expression(self):
        code = 'int x;\nx = y + 2;'
        ast, errors = compile_source(code)
        assert len(errors) >= 1
        assert 'undeclared' in str(errors[0]).lower()

    def test_scope_checking_in_if(self):
        code = 'int a;\na = 5;\nif a > 3 then { int b; b = 1; }\nb = 2;'
        ast, errors = compile_source(code)
        assert len(errors) >= 1


class TestCompiler:
    def test_full_compilation(self):
        code = 'int x;\nint y;\nx = 5;\ny = x + 3;'
        ast, errors = compile_source(code)
        assert ast is not None
        assert len(errors) == 0
        assert len(ast.statements) == 4

    def test_complex_program(self):
        code = 'int a;\nint b;\nint result;\na = 10;\nb = 5;\nif a > b then {\nresult = a - b;\n} else {\nresult = b - a;\n}'
        ast, errors = compile_source(code)
        assert ast is not None
        assert len(errors) == 0

    def test_string_program(self):
        code = 'string greeting;\nstring name;\ngreeting = "hello";\nname = "world";'
        ast, errors = compile_source(code)
        assert ast is not None
        assert len(errors) == 0

    def test_pdf_control_structure(self):
        code = 'int x;\nx = 15;\nif x > 10 then {\nx = x - 1;\n}'
        ast, errors = compile_source(code)
        assert ast is not None
        assert len(errors) == 0

    def test_while_compilation(self):
        code = 'int x;\nx = 10;\nwhile x > 0 {\nx = x - 1;\n}'
        ast, errors = compile_source(code)
        assert ast is not None
        assert len(errors) == 0


if __name__ == '__main__':
    test_classes = [TestLexer, TestParser, TestSemanticAnalyzer, TestCompiler]
    total = passed = failed = 0

    for cls in test_classes:
        print(f"\n{'='*50}")
        print(f"Running {cls.__name__}")
        print('='*50)
        obj = cls()
        for method_name in dir(obj):
            if method_name.startswith('test_'):
                total += 1
                try:
                    getattr(obj, method_name)()
                    print(f"  {method_name}: PASS")
                    passed += 1
                except AssertionError as e:
                    print(f"  {method_name}: FAIL - {e}")
                    failed += 1
                except Exception as e:
                    print(f"  {method_name}: ERROR - {e}")
                    failed += 1

    print(f"\n{'='*50}")
    print(f"Results: {passed}/{total} passed, {failed} failed")
    print('='*50)