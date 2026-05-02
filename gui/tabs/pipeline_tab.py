from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QTextEdit,
    QPushButton, QTreeWidget, QTreeWidgetItem, QHeaderView, QLabel
)
from PyQt5.QtGui import QFont, QBrush, QColor

from src.lexer import tokenize
from src.parser import parse
from src.semantic_analyzer import SemanticAnalyzer
from src.error_handler import ErrorHandler
from gui.syntax_highlighter import SyntaxHighlighter


class PipelineTab(QWidget):
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
        self.compile_btn = QPushButton("Compile")
        self.compile_btn.clicked.connect(self.compile)
        btn_layout.addWidget(self.compile_btn)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)

        # ── Status banner ─────────────────────────────────────────────────
        self.status_label = QLabel()
        self.status_label.setWordWrap(True)
        self.status_label.hide()
        layout.addWidget(self.status_label)

        # ── Pipeline tree ─────────────────────────────────────────────────
        pipeline_group = QGroupBox("Compilation pipeline")
        pipeline_layout = QVBoxLayout(pipeline_group)
        self.pipeline_tree = QTreeWidget()
        self.pipeline_tree.setHeaderLabels(["Phase", "Status", "Details"])
        self.pipeline_tree.setAlternatingRowColors(True)
        self.pipeline_tree.header().setSectionResizeMode(QHeaderView.Interactive)
        self.pipeline_tree.header().setStretchLastSection(True)
        self.pipeline_tree.setColumnWidth(0, 200)
        self.pipeline_tree.setColumnWidth(1, 90)
        pipeline_layout.addWidget(self.pipeline_tree)
        layout.addWidget(pipeline_group)

    # ------------------------------------------------------------------ compile

    def compile(self):
        source = self.source_edit.toPlainText()
        if not source.strip():
            return

        self.pipeline_tree.clear()
        self.status_label.hide()

        root = QTreeWidgetItem(self.pipeline_tree)
        root.setText(0, "Compilation pipeline")
        root.setExpanded(True)

        error_handler = ErrorHandler()

        # ── Phase 1: Lexing ───────────────────────────────────────────────
        lex_item = QTreeWidgetItem(root)
        lex_item.setText(0, "1. Lexical analysis")
        lex_item.setExpanded(True)

        tokens = tokenize(source, error_handler)

        if error_handler.has_errors():
            self._mark(lex_item, False)
            for error in error_handler.get_errors():
                self._add_detail(lex_item, str(error))
            self._set_status(f"Stopped at lexical analysis — {len(error_handler.get_errors())} error(s).", error=True)
            return

        if self._highlighter:
            self._highlighter.set_tokens(tokens)

        self._mark(lex_item, True)
        self._add_detail(lex_item, f"Generated {len(tokens) - 1} tokens")

        # ── Phase 2: Parsing ──────────────────────────────────────────────
        parse_item = QTreeWidgetItem(root)
        parse_item.setText(0, "2. Syntax analysis")
        parse_item.setExpanded(True)

        ast = parse(tokens, error_handler)

        if error_handler.has_errors():
            self._mark(parse_item, False)
            for error in error_handler.get_errors():
                self._add_detail(parse_item, str(error))
            self._set_status(f"Stopped at syntax analysis — {len(error_handler.get_errors())} error(s).", error=True)
            return

        self._mark(parse_item, True)
        self._add_detail(parse_item, f"Built AST with {len(ast.statements)} statement(s)")

        # ── Phase 3: Semantic analysis ────────────────────────────────────
        sem_item = QTreeWidgetItem(root)
        sem_item.setText(0, "3. Semantic analysis")
        sem_item.setExpanded(True)

        analyzer = SemanticAnalyzer(error_handler)
        analyzer.analyze(ast)

        if error_handler.has_errors():
            self._mark(sem_item, False)
            for error in error_handler.get_errors():
                self._add_detail(sem_item, str(error))
            self._set_status(f"Stopped at semantic analysis — {len(error_handler.get_errors())} error(s).", error=True)
            return

        total_symbols = sum(len(s) for s in analyzer.symbol_table.scopes)
        self._mark(sem_item, True)
        self._add_detail(
            sem_item,
            f"Checked {total_symbols} symbol(s) across {len(analyzer.symbol_table.scopes)} scope(s)"
        )

        # ── Done ──────────────────────────────────────────────────────────
        done = QTreeWidgetItem(root)
        done.setText(0, "Compilation complete")
        done.setText(1, "SUCCESS")
        done.setForeground(0, QBrush(QColor("#00cc66")))
        done.setForeground(1, QBrush(QColor("#00cc66")))
        self._set_status("Compilation successful — no errors.", error=False)

    # ------------------------------------------------------------------ helpers

    @staticmethod
    def _mark(item: QTreeWidgetItem, ok: bool):
        colour = QColor("#00cc66") if ok else QColor("#ff4444")
        text   = "SUCCESS" if ok else "FAILED"
        item.setText(1, text)
        item.setForeground(1, QBrush(colour))

    @staticmethod
    def _add_detail(parent: QTreeWidgetItem, text: str):
        child = QTreeWidgetItem(parent)
        child.setText(2, text)

    def _set_status(self, msg: str, error: bool):
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
