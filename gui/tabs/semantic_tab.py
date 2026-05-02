from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QTextEdit,
    QPushButton, QSplitter, QTableWidget, QTableWidgetItem,
    QHeaderView, QLabel
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

from src.lexer import tokenize
from src.parser import parse
from src.semantic_analyzer import SemanticAnalyzer
from src.error_handler import ErrorHandler
from gui.widgets.symbol_table_widget import SymbolTableWidget
from gui.syntax_highlighter import SyntaxHighlighter


class SemanticAnalyzerTab(QWidget):
    def __init__(self):
        super().__init__()
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

        self._highlighter = SyntaxHighlighter(self.source_edit.document())

        # ── Buttons ───────────────────────────────────────────────────────
        btn_layout = QHBoxLayout()
        self.analyze_btn = QPushButton("Analyze")
        self.analyze_btn.clicked.connect(self.analyze)
        btn_layout.addWidget(self.analyze_btn)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)

        # ── Status banner ─────────────────────────────────────────────────
        self.status_label = QLabel()
        self.status_label.setWordWrap(True)
        self.status_label.hide()
        layout.addWidget(self.status_label)

        # ── Symbol table + errors side by side ────────────────────────────
        splitter = QSplitter(Qt.Horizontal)

        symbol_group = QGroupBox("Symbol table")
        symbol_layout = QVBoxLayout(symbol_group)
        self.symbol_table_widget = SymbolTableWidget()
        symbol_layout.addWidget(self.symbol_table_widget)

        errors_group = QGroupBox("Semantic errors")
        errors_layout = QVBoxLayout(errors_group)
        self.errors_table = QTableWidget()
        self.errors_table.setColumnCount(3)
        self.errors_table.setHorizontalHeaderLabels(["Line", "Column", "Error"])
        self.errors_table.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        self.errors_table.horizontalHeader().setStretchLastSection(True)
        self.errors_table.setAlternatingRowColors(True)
        self.errors_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.errors_table.setSelectionBehavior(QTableWidget.SelectRows)
        errors_layout.addWidget(self.errors_table)

        splitter.addWidget(symbol_group)
        splitter.addWidget(errors_group)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 1)
        layout.addWidget(splitter)

    # ------------------------------------------------------------------ analyze

    def analyze(self):
        source = self.source_edit.toPlainText()
        if not source.strip():
            return

        self.status_label.hide()
        error_handler = ErrorHandler()
        tokens = tokenize(source, error_handler)

        if error_handler.has_errors():
            self._show_status(
                "Lexical errors: " + "  |  ".join(str(e) for e in error_handler.get_errors()),
                error=True
            )
            return

        if self._highlighter:
            self._highlighter.set_tokens(tokens)

        ast = parse(tokens, error_handler)

        if error_handler.has_errors():
            self._show_status(
                "Syntax errors: " + "  |  ".join(str(e) for e in error_handler.get_errors()),
                error=True
            )
            return

        analyzer = SemanticAnalyzer(error_handler)
        analyzer.analyze(ast)

        self.symbol_table_widget.update_from_symbol_table(analyzer.symbol_table)

        self.errors_table.setRowCount(0)
        for error in error_handler.get_errors():
            row = self.errors_table.rowCount()
            self.errors_table.insertRow(row)
            self.errors_table.setItem(row, 0, QTableWidgetItem(str(error.line) if error.line else ""))
            self.errors_table.setItem(row, 1, QTableWidgetItem(str(error.column) if error.column else ""))
            self.errors_table.setItem(row, 2, QTableWidgetItem(error.message))

        if error_handler.has_errors():
            self._show_status(
                f"{len(error_handler.get_errors())} semantic error(s) found.",
                error=True
            )
        else:
            self._show_status("Semantic analysis completed successfully — no errors.", error=False)

    # ------------------------------------------------------------------ helpers

    def _show_status(self, msg: str, error: bool):
        if error:
            style = ("background-color: #3a0000; color: #ff8080;"
                     "padding: 6px; border-radius: 4px; font-family: Consolas;")
        else:
            style = ("background-color: #003a00; color: #80ff80;"
                     "padding: 6px; border-radius: 4px; font-family: Consolas;")
        self.status_label.setStyleSheet(style)
        self.status_label.setText(msg)
        self.status_label.show()

    # ------------------------------------------------------------------ shared

    def set_source(self, source: str):
        self.source_edit.setPlainText(source)
