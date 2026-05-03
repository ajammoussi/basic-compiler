import sys
import os

from PyQt5.QtWidgets import (
    QMainWindow, QTabWidget, QVBoxLayout,
    QWidget, QLabel, QHBoxLayout, QComboBox, QStatusBar
)
from PyQt5.QtCore import Qt

from gui.tabs.lexer_tab import LexerTab
from gui.tabs.parser_tab import ParserTab
from gui.tabs.semantic_tab import SemanticAnalyzerTab
from gui.tabs.pipeline_tab import PipelineTab


class CompilerGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Basic Compiler")
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
            QTabBar::tab:hover:!selected {
                background-color: #3c3c3c;
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
            QPushButton:disabled {
                background-color: #3c3c3c;
                color: #888888;
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
            QScrollBar:vertical {
                background: #2d2d2d;
                width: 10px;
            }
            QScrollBar::handle:vertical {
                background: #555555;
                border-radius: 5px;
            }
            QStatusBar {
                background-color: #007acc;
                color: #ffffff;
                font-size: 12px;
            }
        """)

        self._all_tabs: list = []
        self.setup_ui()

    # ------------------------------------------------------------------ UI

    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # Header
        header = QLabel("Basic Compiler")
        header.setStyleSheet("""
            QLabel {
                font-size: 22px;
                font-weight: bold;
                color: #ffffff;
                padding: 10px;
                background-color: #0078d4;
                border-radius: 4px;
            }
        """)
        header.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(header)

        # Example selector
        main_layout.addLayout(self._build_example_bar())

        # Tabs
        self.tabs = QTabWidget()

        self.lexer_tab    = LexerTab()
        self.parser_tab   = ParserTab()
        self.semantic_tab = SemanticAnalyzerTab()
        self.pipeline_tab = PipelineTab()

        self._all_tabs = [
            self.lexer_tab,
            self.parser_tab,
            self.semantic_tab,
            self.pipeline_tab,
        ]

        self.tabs.addTab(self.lexer_tab,    "Lexer")
        self.tabs.addTab(self.parser_tab,   "Parser")
        self.tabs.addTab(self.semantic_tab, "Semantic analyzer")
        self.tabs.addTab(self.pipeline_tab, "Pipeline")

        main_layout.addWidget(self.tabs)

        # Status bar
        status_bar = QStatusBar()
        self.setStatusBar(status_bar)
        status_bar.showMessage("Ready")

    def _build_example_bar(self) -> QHBoxLayout:
        self._examples = {
            "Basic assignment":       "int x;\nx = 5 + 2;",
            "Arithmetic":             "int a;\nint b;\nint result;\na = 10;\nb = 5;\nresult = a * (b + 3) - 2;",
            "If-else (braces)":       "int a;\nint b;\nint result;\na = 10;\nb = 5;\nif a > b then {\n    result = a - b;\n} else {\n    result = b - a;\n}",
            "Inline if-else":         "int a;\nint b;\na = 3;\nb = 7;\nif a > b then a = a + 1; else b = b - 1;",
            "While loop":             "int x;\nx = 10;\nwhile x > 0 {\n    x = x - 1;\n}",
            "String operations":      'string greeting;\nstring name;\ngreeting = "hello";\nname = "world";',
            "String concatenation":   'string s;\ns = "hello" + " world!";',
            "Type mismatch error":    'int x;\nx = "hello";',
            "Undeclared variable":    "x = 5;",
            "Duplicate declaration":  "int x;\nint x;",
        }

        combo = QComboBox()
        combo.addItem("Load an example…")
        combo.addItems(list(self._examples.keys()))
        combo.setStyleSheet("""
            QComboBox {
                background-color: #2d2d2d;
                color: #d4d4d4;
                border: 1px solid #3c3c3c;
                padding: 5px;
                border-radius: 4px;
                min-width: 220px;
            }
            QComboBox::drop-down { border: none; }
            QComboBox QAbstractItemView {
                background-color: #2d2d2d;
                color: #d4d4d4;
                selection-background-color: #0078d4;
            }
        """)
        combo.currentTextChanged.connect(
            lambda name: self._load_example(name) if name != "Load an example…" else None
        )

        lbl = QLabel("Examples:")
        lbl.setStyleSheet("color: #d4d4d4; font-weight: bold;")

        row = QHBoxLayout()
        row.addWidget(lbl)
        row.addWidget(combo)
        row.addStretch()
        return row

    # ------------------------------------------------------------------ helpers

    def _load_example(self, name: str):
        """Push the selected example source to ALL tabs at once (FIX)."""
        source = self._examples.get(name, "")
        if not source:
            return
        for tab in self._all_tabs:
            if hasattr(tab, 'set_source'):
                tab.set_source(source)
        self.statusBar().showMessage(f"Loaded example: {name}")
