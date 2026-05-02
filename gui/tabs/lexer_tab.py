from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QTextEdit,
    QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, QLabel
)
from PyQt5.QtGui import QFont, QColor
from PyQt5.QtCore import Qt

from src.lexer import tokenize, TokenType
from src.error_handler import ErrorHandler
from gui.syntax_highlighter import SyntaxHighlighter


class LexerTab(QWidget):
    def __init__(self):
        super().__init__()
        self._tokens = []
        self._highlighter = None
        self.setup_ui()

    # ------------------------------------------------------------------ UI

    def setup_ui(self):
        layout = QVBoxLayout(self)

        # ── Source editor ─────────────────────────────────────────────────
        source_group = QGroupBox("Source code")
        source_layout = QVBoxLayout(source_group)
        self.source_edit = QTextEdit()
        self.source_edit.setPlaceholderText("Enter source code here…")
        self.source_edit.setFont(QFont("Consolas", 11))
        source_layout.addWidget(self.source_edit)
        layout.addWidget(source_group)

        # Attach syntax highlighter
        self._highlighter = SyntaxHighlighter(self.source_edit.document())

        # ── Buttons ───────────────────────────────────────────────────────
        btn_layout = QHBoxLayout()
        self.tokenize_btn = QPushButton("Tokenize")
        self.tokenize_btn.clicked.connect(self.tokenize)
        btn_layout.addWidget(self.tokenize_btn)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)

        # ── Inline error panel ────────────────────────────────────────────
        self.error_label = QLabel()
        self.error_label.setWordWrap(True)
        self.error_label.setStyleSheet(
            "background-color: #3a0000; color: #ff8080;"
            "padding: 6px; border-radius: 4px; font-family: Consolas;"
        )
        self.error_label.hide()
        layout.addWidget(self.error_label)

        # ── Token table ───────────────────────────────────────────────────
        tokens_group = QGroupBox("Token stream")
        tokens_layout = QVBoxLayout(tokens_group)
        self.tokens_table = QTableWidget()
        self.tokens_table.setColumnCount(4)
        self.tokens_table.setHorizontalHeaderLabels(["Line", "Column", "Type", "Value"])
        self.tokens_table.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        self.tokens_table.horizontalHeader().setStretchLastSection(True)
        self.tokens_table.setAlternatingRowColors(True)
        self.tokens_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tokens_table.setSelectionBehavior(QTableWidget.SelectRows)
        tokens_layout.addWidget(self.tokens_table)
        tokens_group.setLayout(tokens_layout)
        layout.addWidget(tokens_group)

    # ------------------------------------------------------------------ tokenize

    def tokenize(self):
        source = self.source_edit.toPlainText()
        if not source.strip():
            return

        self.error_label.hide()
        error_handler = ErrorHandler()
        self._tokens = tokenize(source, error_handler)

        # Highlight the source text
        if self._highlighter:
            self._highlighter.set_tokens(self._tokens)

        # Populate the token table
        self.tokens_table.setRowCount(0)

        # Colour map by category
        type_colours = {
            "KW_":      QColor("#569cd6"),
            "IDENT":    QColor("#9cdcfe"),
            "NUMBER":   QColor("#b5cea8"),
            "STRING":   QColor("#ce9178"),
        }

        for token in self._tokens:
            if token.type == TokenType.EOF:
                continue

            row = self.tokens_table.rowCount()
            self.tokens_table.insertRow(row)

            items = [
                QTableWidgetItem(str(token.line)),
                QTableWidgetItem(str(token.column)),
                QTableWidgetItem(token.type.name),
                QTableWidgetItem(token.value),
            ]

            # Colour the Type cell
            colour = None
            name = token.type.name
            if name.startswith("KW_"):
                colour = type_colours["KW_"]
            elif name == "IDENTIFIER":
                colour = type_colours["IDENT"]
            elif name == "NUMBER":
                colour = type_colours["NUMBER"]
            elif name == "STRING_LITERAL":
                colour = type_colours["STRING"]

            for col, item in enumerate(items):
                if colour and col == 2:
                    item.setForeground(colour)
                self.tokens_table.setItem(row, col, item)

        # Show errors inline
        if error_handler.has_errors():
            msgs = "\n".join(str(e) for e in error_handler.get_errors())
            self.error_label.setText(f"Lexical errors:\n{msgs}")
            self.error_label.show()

    # ------------------------------------------------------------------ shared

    def set_source(self, source: str):
        self.source_edit.setPlainText(source)
