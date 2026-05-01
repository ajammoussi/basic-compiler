import sys
import os

from PyQt5.QtWidgets import (QMainWindow, QTabWidget, QVBoxLayout,
                             QWidget, QLabel, QHBoxLayout, QComboBox)
from PyQt5.QtCore import Qt

from gui.tabs.lexer_tab import LexerTab
from gui.tabs.parser_tab import ParserTab
from gui.tabs.semantic_tab import SemanticAnalyzerTab
from gui.tabs.pipeline_tab import PipelineTab

class CompilerGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Basic Compiler - Interactive GUI")
        self.setGeometry(100, 100, 1400, 900)
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1e1e1e;
            }
            QWidget {
                background-color: #1e1e1e;
                color: #d4d4d4;
            }
            QTabWidget::pane {
                border: 1px solid #3c3c3c;
                background-color: #1e1e1e;
            }
            QTabBar::tab {
                background-color: #2d2d2d;
                color: #d4d4d4;
                padding: 8px 16px;
                margin-right: 2px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }
            QTabBar::tab:selected {
                background-color: #0078d4;
                color: white;
            }
            QGroupBox {
                color: #ffffff;
                font-weight: bold;
                border: 1px solid #3c3c3c;
                border-radius: 4px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
            QLabel {
                color: #d4d4d4;
                background-color: transparent;
            }
            QPushButton {
                background-color: #0078d4;
                color: white;
                border: none;
                padding: 8px 16px;
                font-size: 12px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #106ebe;
            }
            QPushButton:pressed {
                background-color: #005a9e;
            }
            QMessageBox {
                background-color: #1e1e1e;
            }
            QMessageBox QLabel {
                color: #d4d4d4;
            }
            QMessageBox QPushButton {
                min-width: 80px;
            }
            QAbstractItemView {
                background-color: #1e1e1e;
                alternate-background-color: #252525;
                color: #d4d4d4;
                gridline-color: #3c3c3c;
                selection-background-color: #0078d4;
                selection-color: white;
                border: 1px solid #3c3c3c;
            }
            QHeaderView::section {
                background-color: #2d2d2d;
                color: #ffffff;
                padding: 4px;
                border: none;
                border-bottom: 1px solid #3c3c3c;
            }
        """)

        self.setup_ui()

    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        self.main_layout = QVBoxLayout(central_widget)

        header = QLabel("Basic Compiler - Interactive Visualization")
        header.setStyleSheet("""
            QLabel {
                font-size: 24px;
                font-weight: bold;
                color: #ffffff;
                padding: 10px;
                background-color: #0078d4;
                border-radius: 4px;
            }
        """)
        header.setAlignment(Qt.AlignCenter)
        self.main_layout.addWidget(header)

        self.tabs = QTabWidget()

        self.lexer_tab = LexerTab()
        self.parser_tab = ParserTab()
        self.semantic_tab = SemanticAnalyzerTab()
        self.pipeline_tab = PipelineTab()

        self.tabs.addTab(self.lexer_tab, "Lexer")
        self.tabs.addTab(self.parser_tab, "Parser")
        self.tabs.addTab(self.semantic_tab, "Semantic Analyzer")
        self.tabs.addTab(self.pipeline_tab, "Pipeline")

        self.main_layout.addWidget(self.tabs)

        self.setup_examples()

    def setup_examples(self):
        examples = {
            "Basic Assignment": "int x;\nx = 5 + 2;",
            "Arithmetic": "int a;\nint b;\nint result;\na = 10;\nb = 5;\nresult = a * (b + c) - d / 2;",
            "Conditional": "int a;\nint b;\nint result;\na = 10;\nb = 5;\nif a > b then {\n    result = a - b;\n} else {\n    result = b - a;\n}",
            "String Operations": 'string greeting;\nstring name;\nstring message;\ngreeting = "hello";\nname = "world";\nmessage = greeting + " " + name;',
            "Simple Expression": "x = 5 + 2;",
            "Complex Expression": "z = x * (y - 3);",
            "Inline If-Else": "if a = b then a = a + 1; else b = b - 1;",
            "Type Mismatch Error": 'int x;\nx = "hello";',
            "Undeclared Variable Error": "x = 5;",
            "String Concatenation": 'string s;\ns = "hello" + " world!";',
        }

        example_combo = QComboBox()
        example_combo.addItems(["Select an example..."] + list(examples.keys()))
        example_combo.setStyleSheet("""
            QComboBox {
                background-color: #2d2d2d;
                color: #d4d4d4;
                border: 1px solid #3c3c3c;
                padding: 5px;
                border-radius: 4px;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox QAbstractItemView {
                background-color: #2d2d2d;
                color: #d4d4d4;
                selection-background-color: #0078d4;
            }
        """)

        example_combo.currentTextChanged.connect(
            lambda name: self.load_example(name, examples) if name != "Select an example..." else None
        )

        example_label = QLabel("Load Example:")
        example_label.setStyleSheet("color: #d4d4d4; font-weight: bold;")

        example_layout = QHBoxLayout()
        example_layout.addWidget(example_label)
        example_layout.addWidget(example_combo)
        example_layout.addStretch()

        self.main_layout.insertLayout(2, example_layout)

    def load_example(self, name, examples):
        source = examples.get(name, "")
        if source:
            current_tab = self.tabs.currentWidget()
            if hasattr(current_tab, 'set_source'):
                current_tab.set_source(source)