from PyQt5.QtWidgets import QWidget, QVBoxLayout, QGroupBox, QTextEdit, QHBoxLayout, QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox
from PyQt5.QtGui import QFont
from src.lexer import tokenize, TokenType
from src.error_handler import ErrorHandler

class LexerTab(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.tokens = []

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
        self.tokenize_btn = QPushButton("Tokenize")
        self.tokenize_btn.setStyleSheet("")
        self.tokenize_btn.clicked.connect(self.tokenize)
        button_layout.addWidget(self.tokenize_btn)
        button_layout.addStretch()

        tokens_group = QGroupBox("Token Stream")
        tokens_layout = QVBoxLayout()
        self.tokens_table = QTableWidget()
        self.tokens_table.setColumnCount(4)
        self.tokens_table.setHorizontalHeaderLabels(["Line", "Column", "Type", "Value"])
        self.tokens_table.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        self.tokens_table.horizontalHeader().setStretchLastSection(True)
        self.tokens_table.setStyleSheet("")
        tokens_layout.addWidget(self.tokens_table)
        tokens_group.setLayout(tokens_layout)

        layout.addWidget(source_group)
        layout.addLayout(button_layout)
        layout.addWidget(tokens_group)
        self.setLayout(layout)

    def tokenize(self):
        source = self.source_edit.toPlainText()
        if not source.strip():
            return

        error_handler = ErrorHandler()
        self.tokens = tokenize(source, error_handler)

        self.tokens_table.setRowCount(0)

        for token in self.tokens:
            if token.type == TokenType.EOF:
                continue

            row = self.tokens_table.rowCount()
            self.tokens_table.insertRow(row)

            self.tokens_table.setItem(row, 0, QTableWidgetItem(str(token.line)))
            self.tokens_table.setItem(row, 1, QTableWidgetItem(str(token.column)))
            self.tokens_table.setItem(row, 2, QTableWidgetItem(token.type.name))
            self.tokens_table.setItem(row, 3, QTableWidgetItem(token.value))

        if error_handler.has_errors():
            QMessageBox.warning(self, "Lexical Errors", "\n".join(str(e) for e in error_handler.get_errors()))

    def set_source(self, source):
        self.source_edit.setPlainText(source)
