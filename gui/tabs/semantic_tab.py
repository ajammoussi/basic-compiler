from PyQt5.QtWidgets import QWidget, QVBoxLayout, QGroupBox, QTextEdit, QHBoxLayout, QPushButton, QSplitter, QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from src.lexer import tokenize
from src.parser import parse
from src.semantic_analyzer import SemanticAnalyzer
from src.error_handler import ErrorHandler
from gui.widgets.symbol_table_widget import SymbolTableWidget

class SemanticAnalyzerTab(QWidget):
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
        self.analyze_btn = QPushButton("Analyze")
        self.analyze_btn.setStyleSheet("")
        self.analyze_btn.clicked.connect(self.analyze)
        button_layout.addWidget(self.analyze_btn)
        button_layout.addStretch()

        tables_splitter = QSplitter(Qt.Horizontal)

        symbol_table_group = QGroupBox("Symbol Table")
        symbol_table_layout = QVBoxLayout()
        self.symbol_table_widget = SymbolTableWidget()
        symbol_table_layout.addWidget(self.symbol_table_widget)
        symbol_table_group.setLayout(symbol_table_layout)

        errors_group = QGroupBox("Semantic Errors")
        errors_layout = QVBoxLayout()
        self.errors_table = QTableWidget()
        self.errors_table.setColumnCount(3)
        self.errors_table.setHorizontalHeaderLabels(["Line", "Column", "Error"])
        self.errors_table.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        self.errors_table.horizontalHeader().setStretchLastSection(True)
        self.errors_table.setStyleSheet("")
        errors_layout.addWidget(self.errors_table)
        errors_group.setLayout(errors_layout)

        tables_splitter.addWidget(symbol_table_group)
        tables_splitter.addWidget(errors_group)
        tables_splitter.setStretchFactor(0, 1)
        tables_splitter.setStretchFactor(1, 1)

        layout.addWidget(source_group)
        layout.addLayout(button_layout)
        layout.addWidget(tables_splitter)
        self.setLayout(layout)

    def analyze(self):
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

        if not error_handler.has_errors():
            QMessageBox.information(self, "Success", "Semantic analysis completed successfully!")

    def set_source(self, source):
        self.source_edit.setPlainText(source)
