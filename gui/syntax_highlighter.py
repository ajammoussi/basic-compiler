from PyQt5.QtGui import QSyntaxHighlighter, QTextCharFormat, QColor, QFont
from src.lexer import TokenType


class SyntaxHighlighter(QSyntaxHighlighter):
    """Token-based syntax highlighter for the shared source editor.

    After tokenization, call set_tokens(tokens) and the editor will
    colour each token according to its type.
    """

    # Colour map: TokenType → (hex colour, bold?)
    _COLOURS = {
        TokenType.KW_IF:       ("#569cd6", True),
        TokenType.KW_THEN:     ("#569cd6", True),
        TokenType.KW_ELSE:     ("#569cd6", True),
        TokenType.KW_WHILE:    ("#569cd6", True),
        TokenType.KW_INT:      ("#c586c0", True),
        TokenType.KW_STRING:   ("#c586c0", True),
        TokenType.IDENTIFIER:  ("#9cdcfe", False),
        TokenType.NUMBER:      ("#b5cea8", False),
        TokenType.STRING_LITERAL: ("#ce9178", False),
        TokenType.PLUS:        ("#d4d4d4", False),
        TokenType.MINUS:       ("#d4d4d4", False),
        TokenType.MULTIPLY:    ("#d4d4d4", False),
        TokenType.DIVIDE:      ("#d4d4d4", False),
        TokenType.GREATER:     ("#d4d4d4", False),
        TokenType.LESS:        ("#d4d4d4", False),
        TokenType.EQUALS:      ("#d4d4d4", False),
        TokenType.LPAREN:      ("#ffd700", False),
        TokenType.RPAREN:      ("#ffd700", False),
        TokenType.LBRACE:      ("#da70d6", False),
        TokenType.RBRACE:      ("#da70d6", False),
        TokenType.SEMICOLON:   ("#808080", False),
    }

    def __init__(self, document, tokens=None):
        super().__init__(document)
        self.tokens = tokens or []
        # Build a per-line lookup: line_number → list of (column, length, format)
        self._line_map: dict[int, list] = {}
        if self.tokens:
            self._build_line_map()

    def set_tokens(self, tokens):
        self.tokens = tokens or []
        self._build_line_map()
        self.rehighlight()

    def _build_line_map(self):
        self._line_map = {}
        for token in self.tokens:
            colour_info = self._COLOURS.get(token.type)
            if colour_info is None:
                continue
            colour, bold = colour_info
            fmt = QTextCharFormat()
            fmt.setForeground(QColor(colour))
            if bold:
                fmt.setFontWeight(QFont.Bold)
            line = token.line  # 1-based
            entry = (token.column - 1, len(token.value), fmt)  # column is 1-based → 0-based offset
            self._line_map.setdefault(line, []).append(entry)

    def highlightBlock(self, text):
        line = self.currentBlockState() + 1  # QTextBlock is 0-based; our tokens are 1-based
        for start, length, fmt in self._line_map.get(line, []):
            if start >= 0 and start < len(text):
                self.setFormat(start, min(length, len(text) - start), fmt)
