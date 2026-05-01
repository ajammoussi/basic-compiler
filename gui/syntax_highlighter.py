from PyQt5.QtGui import QSyntaxHighlighter, QTextCharFormat, QColor, QFont
from src.lexer import TokenType

class SyntaxHighlighter(QSyntaxHighlighter):
    def __init__(self, document, tokens=None):
        super().__init__(document)
        self.tokens = tokens or []
        self.highlighting_rules = []

    def set_tokens(self, tokens):
        self.tokens = tokens
        self.rehighlight()

    def highlightBlock(self, text):
        if not self.tokens:
            return

        block_text = self.currentBlock().text()

        for token in self.tokens:
            if token.line == self.currentBlockNumber() + 1:
                start = token.column
                length = len(token.value)

                if start < len(block_text):
                    format = QTextCharFormat()

                    if token.type == TokenType.KW_IF or token.type == TokenType.KW_THEN or token.type == TokenType.KW_ELSE:
                        format.setForeground(QColor("#0000FF"))
                        format.setFontWeight(QFont.Bold)
                    elif token.type == TokenType.KW_INT or token.type == TokenType.KW_STRING:
                        format.setForeground(QColor("#800080"))
                        format.setFontWeight(QFont.Bold)
                    elif token.type == TokenType.IDENTIFIER:
                        format.setForeground(QColor("#008000"))
                    elif token.type == TokenType.NUMBER:
                        format.setForeground(QColor("#FF0000"))
                    elif token.type == TokenType.STRING_LITERAL:
                        format.setForeground(QColor("#FF00FF"))
                    elif token.type in (TokenType.PLUS, TokenType.MINUS, TokenType.MULTIPLY, TokenType.DIVIDE):
                        format.setForeground(QColor("#FF8C00"))
                    elif token.type in (TokenType.GREATER, TokenType.LESS, TokenType.EQUALS):
                        format.setForeground(QColor("#FF8C00"))
                    elif token.type in (TokenType.LPAREN, TokenType.RPAREN, TokenType.LBRACE, TokenType.RBRACE):
                        format.setForeground(QColor("#808080"))
                    elif token.type == TokenType.SEMICOLON:
                        format.setForeground(QColor("#808080"))

                    self.setFormat(start, length, format)
