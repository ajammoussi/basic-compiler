from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox,
    QTextEdit, QPushButton, QTabWidget, QMessageBox, QLabel
)
from PyQt5.QtGui import QFont

from src.lexer import tokenize
from src.parser import parse
from src.error_handler import ErrorHandler
from src.lr_parser_trace import build_trace

from gui.widgets.parse_tree_widget import ParseTreeWidget
from gui.widgets.ast_canvas_widget import ASTCanvasWidget
from gui.widgets.bottom_up_widget import BottomUpWidget
from gui.syntax_highlighter import SyntaxHighlighter


class ParserTab(QWidget):
    def __init__(self):
        super().__init__()
        self._ast = None
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

        # Attach syntax highlighter
        self._highlighter = SyntaxHighlighter(self.source_edit.document())

        layout.addWidget(source_group)

        # ── Buttons ───────────────────────────────────────────────────────
        btn_layout = QHBoxLayout()
        self.parse_btn = QPushButton("Parse")
        self.parse_btn.clicked.connect(self.parse)
        btn_layout.addWidget(self.parse_btn)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)

        # ── Sub-tab panel ─────────────────────────────────────────────────
        self.sub_tabs = QTabWidget()

        # 1. Top-down tree
        self.tree_widget = ParseTreeWidget()
        self.sub_tabs.addTab(self.tree_widget, "Top-down tree")

        # 2. Graphical canvas
        self.canvas_widget = ASTCanvasWidget()
        self.sub_tabs.addTab(self.canvas_widget, "Graphical tree")

        # 3. Bottom-up trace
        self.bottom_up_widget = BottomUpWidget()
        self.sub_tabs.addTab(self.bottom_up_widget, "Bottom-up trace")

        layout.addWidget(self.sub_tabs)

    # ------------------------------------------------------------------ parse

    def parse(self):
        source = self.source_edit.toPlainText()
        if not source.strip():
            return

        error_handler = ErrorHandler()
        tokens = tokenize(source, error_handler)

        if error_handler.has_errors():
            QMessageBox.warning(
                self, "Lexical errors",
                "\n".join(str(e) for e in error_handler.get_errors())
            )
            return

        # Update syntax highlighting
        if self._highlighter:
            self._highlighter.set_tokens(tokens)

        ast = parse(tokens, error_handler)

        if error_handler.has_errors():
            QMessageBox.warning(
                self, "Syntax errors",
                "\n".join(str(e) for e in error_handler.get_errors())
            )
            return

        self._ast = ast

        # 1. Top-down tree
        self.tree_widget.clear()
        self.tree_widget.build_tree(ast)

        # 2. Graphical canvas
        self.canvas_widget.display_ast(ast)

        # 3. Bottom-up trace
        try:
            steps = build_trace(ast, tokens)
            self.bottom_up_widget.load_steps(steps)
        except Exception as exc:
            self.bottom_up_widget.clear()
            # Non-fatal: tree views still work
            print(f"[bottom-up trace] {exc}")

    # ------------------------------------------------------------------ shared editor

    def set_source(self, source: str):
        """Called by MainWindow when the user picks an example."""
        self.source_edit.setPlainText(source)
