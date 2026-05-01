class CompilerError(Exception):
    def __init__(self, message, line=None, column=None):
        self.message = message
        self.line = line
        self.column = column
        super().__init__(self._format_message())

    def _format_message(self):
        if self.line is not None:
            location = f"Line {self.line}"
            if self.column is not None:
                location += f", Column {self.column}"
            return f"{location}: {self.message}"
        return self.message


class LexerError(CompilerError):
    pass


class ParserError(CompilerError):
    pass


class SemanticError(CompilerError):
    pass


class ErrorHandler:
    def __init__(self):
        self.errors = []
        self.warnings = []

    def add_error(self, message, line=None, column=None):
        self.errors.append(LexerError(message, line, column))

    def add_parser_error(self, message, line=None, column=None):
        self.errors.append(ParserError(message, line, column))

    def add_semantic_error(self, message, line=None, column=None):
        self.errors.append(SemanticError(message, line, column))

    def add_warning(self, message, line=None, column=None):
        self.warnings.append(CompilerError(message, line, column))

    def has_errors(self):
        return len(self.errors) > 0

    def get_errors(self):
        return self.errors

    def print_errors(self):
        for error in self.errors:
            print(f"ERROR: {error}", file=__import__('sys').stderr)

    def clear(self):
        self.errors = []
        self.warnings = []