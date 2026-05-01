from .lexer import tokenize, Lexer, TokenType
from .parser import parse, Parser
from .semantic_analyzer import SemanticAnalyzer
from .error_handler import ErrorHandler
from .ast_nodes import Program


class Compiler:
    def __init__(self):
        self.error_handler = ErrorHandler()

    def compile(self, source_code):
        self.error_handler.clear()
        tokens = tokenize(source_code, self.error_handler)
        ast = parse(tokens, self.error_handler)
        if self.error_handler.has_errors():
            return None, self.error_handler.get_errors()
        analyzer = SemanticAnalyzer(self.error_handler)
        analyzer.analyze(ast)
        if self.error_handler.has_errors():
            return None, self.error_handler.get_errors()
        return ast, []

    def compile_file(self, file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            source = f.read()
        return self.compile(source)


def compile_source(source_code):
    compiler = Compiler()
    return compiler.compile(source_code)


def compile_file(file_path):
    compiler = Compiler()
    return compiler.compile_file(file_path)