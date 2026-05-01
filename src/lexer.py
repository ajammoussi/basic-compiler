from enum import Enum, auto
import re
from .error_handler import LexerError


class TokenType(Enum):
    KW_IF = auto()
    KW_THEN = auto()
    KW_ELSE = auto()
    KW_WHILE = auto()
    KW_INT = auto()
    KW_STRING = auto()
    IDENTIFIER = auto()
    NUMBER = auto()
    STRING_LITERAL = auto()
    PLUS = auto()
    MINUS = auto()
    EQUALS = auto()
    GREATER = auto()
    LESS = auto()
    MULTIPLY = auto()
    DIVIDE = auto()
    LPAREN = auto()
    RPAREN = auto()
    LBRACE = auto()
    RBRACE = auto()
    SEMICOLON = auto()
    EOF = auto()
    UNKNOWN = auto()


KEYWORDS = {
    'if': TokenType.KW_IF,
    'then': TokenType.KW_THEN,
    'else': TokenType.KW_ELSE,
    'while': TokenType.KW_WHILE,
    'int': TokenType.KW_INT,
    'string': TokenType.KW_STRING,
}


class Token:
    def __init__(self, token_type, value, line=1, column=0):
        self.type = token_type
        self.value = value
        self.line = line
        self.column = column

    def __repr__(self):
        if self.type == TokenType.IDENTIFIER:
            return f"ID('{self.value}')"
        elif self.type == TokenType.NUMBER:
            return f"NUM({self.value})"
        elif self.type == TokenType.STRING_LITERAL:
            return f"STR({self.value})"
        elif self.type in (TokenType.KW_IF, TokenType.KW_THEN, TokenType.KW_ELSE,
                           TokenType.KW_INT, TokenType.KW_STRING, TokenType.KW_WHILE):
            return f"KW('{self.value}')"
        else:
            return f"'{self.value}'"


class Lexer:
    TOKEN_PATTERNS = [
        (r'int\b', TokenType.KW_INT),
        (r'string\b', TokenType.KW_STRING),
        (r'if\b', TokenType.KW_IF),
        (r'then\b', TokenType.KW_THEN),
        (r'else\b', TokenType.KW_ELSE),
        (r'while\b', TokenType.KW_WHILE),
        (r'[a-zA-Z_][a-zA-Z0-9_]*', TokenType.IDENTIFIER),
        (r'\d+', TokenType.NUMBER),
        (r'"[^"]*"', TokenType.STRING_LITERAL),
        (r'\+', TokenType.PLUS),
        (r'-', TokenType.MINUS),
        (r'=', TokenType.EQUALS),
        (r'>', TokenType.GREATER),
        (r'<', TokenType.LESS),
        (r'\*', TokenType.MULTIPLY),
        (r'/', TokenType.DIVIDE),
        (r'\(', TokenType.LPAREN),
        (r'\)', TokenType.RPAREN),
        (r'\{', TokenType.LBRACE),
        (r'\}', TokenType.RBRACE),
        (r';', TokenType.SEMICOLON),
        (r'[ \t\r\n]+', None),
    ]

    def __init__(self, source_code, error_handler=None):
        self.source = source_code
        self.pos = 0
        self.line = 1
        self.column = 0
        self.tokens = []
        self.error_handler = error_handler

    def tokenize(self):
        self.pos = 0
        self.line = 1
        self.column = 0
        self.tokens = []

        while self.pos < len(self.source):
            matched = False
            for pattern, token_type in self.TOKEN_PATTERNS:
                regex = re.compile(pattern)
                match = regex.match(self.source, self.pos)
                if match:
                    token_text = match.group(0)
                    if token_type is not None:
                        if token_type == TokenType.IDENTIFIER and token_text in KEYWORDS:
                            token_type = KEYWORDS[token_text]
                        token = Token(token_type, token_text, self.line, self.column)
                        self.tokens.append(token)
                    self._advance(token_text)
                    matched = True
                    break

            if not matched:
                if self.error_handler:
                    self.error_handler.add_error(
                        f"Unexpected character: {self.source[self.pos]!r}",
                        self.line, self.column
                    )
                self._advance(1)

        self.tokens.append(Token(TokenType.EOF, '', self.line, self.column))
        return self.tokens

    def _advance(self, text):
        for char in text:
            if char == '\n':
                self.line += 1
                self.column = 0
            else:
                self.column += 1
        self.pos += len(text)


def tokenize(source_code, error_handler=None):
    lexer = Lexer(source_code, error_handler)
    return lexer.tokenize()