from PyQt5.QtWidgets import QWidget, QVBoxLayout, QGroupBox, QTextEdit, QHBoxLayout, QPushButton, QMessageBox
from PyQt5.QtGui import QFont
from src.lexer import tokenize
from src.parser import parse
from src.error_handler import ErrorHandler
from gui.widgets.parse_tree_widget import ParseTreeWidget

class ParserTab(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()

        source_group = QGroupBox("Source Code")
        source_layout = QVBoxLayout()
        self.source_edit = QTextEdit()
        self.source_edit.setPlaceholderText("Enter source code here...")
        self.source_edit.setFont(QFont("Consolas", 11))
        self.source_edit.setStyleSheet("")
        source_layout.addWidget(self.source_edit)
        source_group.setLayout(source_layout)

        button_layout = QHBoxLayout()
        self.parse_btn = QPushButton("Parse")
        self.parse_btn.setStyleSheet("")
        self.parse_btn.clicked.connect(self.parse)
        button_layout.addWidget(self.parse_btn)
        button_layout.addStretch()

        tree_group = QGroupBox("Parse Tree (AST)")
        tree_layout = QVBoxLayout()
        self.tree_widget = ParseTreeWidget()
        tree_layout.addWidget(self.tree_widget)
        tree_group.setLayout(tree_layout)

        layout.addWidget(source_group)
        layout.addLayout(button_layout)
        layout.addWidget(tree_group)
        self.setLayout(layout)

    def parse(self):
        source = self.source_edit.toPlainText()
        if not source.strip():
            return

        error_handler = ErrorHandler()
        tokens = tokenize(source, error_handler)

        if error_handler.has_errors():
            QMessageBox.warning(self, "Lexical Errors", "\n".join(str(e) for e in error_handler.get_errors()))
            return

        ast = parse(tokens, error_handler)

        if error_handler.has_errors():
            QMessageBox.warning(self, "Syntax Errors", "\n".join(str(e) for e in error_handler.get_errors()))
            return

        self.tree_widget.clear()
        self.tree_widget.build_tree(ast)

    def set_source(self, source):
        self.source_edit.setPlainText(source)
