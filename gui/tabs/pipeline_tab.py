from PyQt5.QtWidgets import QWidget, QVBoxLayout, QGroupBox, QTextEdit, QHBoxLayout, QPushButton, QTreeWidget, QTreeWidgetItem, QHeaderView
from PyQt5.QtGui import QFont, QBrush, QColor
from src.lexer import tokenize
from src.parser import parse
from src.semantic_analyzer import SemanticAnalyzer
from src.error_handler import ErrorHandler

class PipelineTab(QWidget):
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
        self.compile_btn = QPushButton("Compile")
        self.compile_btn.setStyleSheet("")
        self.compile_btn.clicked.connect(self.compile)
        button_layout.addWidget(self.compile_btn)
        button_layout.addStretch()

        pipeline_group = QGroupBox("Compilation Pipeline")
        pipeline_layout = QVBoxLayout()

        self.pipeline_tree = QTreeWidget()
        self.pipeline_tree.setHeaderLabels(["Phase", "Status", "Details"])
        self.pipeline_tree.setAlternatingRowColors(True)
        self.pipeline_tree.header().setSectionResizeMode(QHeaderView.Interactive)
        self.pipeline_tree.header().setStretchLastSection(True)
        pipeline_layout.addWidget(self.pipeline_tree)
        pipeline_group.setLayout(pipeline_layout)

        layout.addWidget(source_group)
        layout.addLayout(button_layout)
        layout.addWidget(pipeline_group)
        self.setLayout(layout)

    def compile(self):
        source = self.source_edit.toPlainText()
        if not source.strip():
            return

        self.pipeline_tree.clear()

        root = QTreeWidgetItem(self.pipeline_tree)
        root.setText(0, "Compilation Pipeline")
        root.setExpanded(True)

        error_handler = ErrorHandler()

        lexer_item = QTreeWidgetItem(root)
        lexer_item.setText(0, "1. Lexical Analysis")
        lexer_item.setExpanded(True)

        tokens = tokenize(source, error_handler)

        if error_handler.has_errors():
            lexer_item.setText(1, "FAILED")
            lexer_item.setForeground(1, QBrush(QColor("#FF0000")))
            for error in error_handler.get_errors():
                err_item = QTreeWidgetItem(lexer_item)
                err_item.setText(2, str(error))
            return
        else:
            lexer_item.setText(1, "SUCCESS")
            lexer_item.setForeground(1, QBrush(QColor("#00FF00")))
            token_count_item = QTreeWidgetItem(lexer_item)
            token_count_item.setText(2, f"Generated {len(tokens) - 1} tokens")

        parser_item = QTreeWidgetItem(root)
        parser_item.setText(0, "2. Syntax Analysis")
        parser_item.setExpanded(True)

        ast = parse(tokens, error_handler)

        if error_handler.has_errors():
            parser_item.setText(1, "FAILED")
            parser_item.setForeground(1, QBrush(QColor("#FF0000")))
            for error in error_handler.get_errors():
                err_item = QTreeWidgetItem(parser_item)
                err_item.setText(2, str(error))
            return
        else:
            parser_item.setText(1, "SUCCESS")
            parser_item.setForeground(1, QBrush(QColor("#00FF00")))
            stmt_count_item = QTreeWidgetItem(parser_item)
            stmt_count_item.setText(2, f"Built AST with {len(ast.statements)} statements")

        semantic_item = QTreeWidgetItem(root)
        semantic_item.setText(0, "3. Semantic Analysis")
        semantic_item.setExpanded(True)

        analyzer = SemanticAnalyzer(error_handler)
        analyzer.analyze(ast)

        if error_handler.has_errors():
            semantic_item.setText(1, "FAILED")
            semantic_item.setForeground(1, QBrush(QColor("#FF0000")))
            for error in error_handler.get_errors():
                err_item = QTreeWidgetItem(semantic_item)
                err_item.setText(2, str(error))
        else:
            semantic_item.setText(1, "SUCCESS")
            semantic_item.setForeground(1, QBrush(QColor("#00FF00")))
            symbol_count_item = QTreeWidgetItem(semantic_item)
            total_symbols = sum(len(scope) for scope in analyzer.symbol_table.scopes)
            symbol_count_item.setText(2, f"Checked {total_symbols} symbols across {len(analyzer.symbol_table.scopes)} scope(s)")

        if not error_handler.has_errors():
            success_item = QTreeWidgetItem(root)
            success_item.setText(0, "Compilation Complete")
            success_item.setText(1, "SUCCESS")
            success_item.setForeground(1, QBrush(QColor("#00FF00")))
            success_item.setForeground(0, QBrush(QColor("#00FF00")))

    def set_source(self, source):
        self.source_edit.setPlainText(source)
