"""
bottom_up_widget.py
-------------------
Displays the shift-reduce derivation trace produced by lr_parser_trace.py
in a colour-coded QTableWidget.

Columns: Step | Action | Symbol | Stack | Lookahead | Rule
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget,
    QTableWidgetItem, QHeaderView, QPushButton, QLabel, QSlider
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QColor, QFont

from src.lr_parser_trace import TraceStep

# Colours
_COL_SHIFT  = QColor("#1a4a6b")   # dark blue bg
_COL_REDUCE = QColor("#3d1a00")   # dark amber bg
_COL_ACCEPT = QColor("#0d3320")   # dark green bg
_COL_FG     = QColor("#f0f0f0")
_MONO       = QFont("Consolas", 10)


class BottomUpWidget(QWidget):
    """
    Shows the shift-reduce trace as an interactive table.

    Features
    --------
    * All steps shown at once with colour coding.
    * "Step through" mode: Previous / Next buttons highlight the current row.
    * Auto-play: runs through all steps with a configurable speed slider.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self._steps: list[TraceStep] = []
        self._current_step = -1
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._auto_next)
        self._setup_ui()

    # ------------------------------------------------------------------ UI

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 4, 0, 0)

        # ── Toolbar ──────────────────────────────────────────────────────
        toolbar = QHBoxLayout()

        self._btn_prev  = QPushButton("◀ Prev")
        self._btn_next  = QPushButton("Next ▶")
        self._btn_play  = QPushButton("▶ Auto-play")
        self._btn_reset = QPushButton("⟳ Reset")

        for btn in (self._btn_prev, self._btn_next, self._btn_play, self._btn_reset):
            btn.setFixedHeight(26)

        self._btn_prev.clicked.connect(self._prev_step)
        self._btn_next.clicked.connect(self._next_step)
        self._btn_play.clicked.connect(self._toggle_play)
        self._btn_reset.clicked.connect(self._reset_step)

        self._step_label = QLabel("Step 0 / 0")
        self._step_label.setFixedWidth(100)

        speed_label = QLabel("Speed:")
        self._speed_slider = QSlider(Qt.Horizontal)
        self._speed_slider.setRange(100, 2000)
        self._speed_slider.setValue(600)
        self._speed_slider.setFixedWidth(120)
        self._speed_slider.setToolTip("Auto-play interval (ms)")
        self._speed_slider.valueChanged.connect(
            lambda v: self._timer.setInterval(v) if self._timer.isActive() else None
        )

        toolbar.addWidget(self._btn_prev)
        toolbar.addWidget(self._btn_next)
        toolbar.addWidget(self._btn_play)
        toolbar.addWidget(self._btn_reset)
        toolbar.addWidget(self._step_label)
        toolbar.addStretch()
        toolbar.addWidget(speed_label)
        toolbar.addWidget(self._speed_slider)

        layout.addLayout(toolbar)

        # ── Legend ───────────────────────────────────────────────────────
        legend = QHBoxLayout()
        for colour, label in (
            (_COL_SHIFT,  "SHIFT"),
            (_COL_REDUCE, "REDUCE"),
            (_COL_ACCEPT, "ACCEPT"),
        ):
            dot = QLabel("■")
            dot.setStyleSheet(f"color: {colour.name()};")
            lbl = QLabel(label)
            lbl.setFont(_MONO)
            legend.addWidget(dot)
            legend.addWidget(lbl)
            legend.addSpacing(12)
        legend.addStretch()
        layout.addLayout(legend)

        # ── Table ────────────────────────────────────────────────────────
        self._table = QTableWidget()
        self._table.setColumnCount(6)
        self._table.setHorizontalHeaderLabels(
            ["Step", "Action", "Symbol", "Stack", "Lookahead", "Rule / Note"]
        )
        self._table.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        self._table.horizontalHeader().setStretchLastSection(True)
        self._table.setColumnWidth(0, 50)
        self._table.setColumnWidth(1, 70)
        self._table.setColumnWidth(2, 80)
        self._table.setColumnWidth(3, 200)
        self._table.setColumnWidth(4, 90)
        self._table.setFont(_MONO)
        self._table.setEditTriggers(QTableWidget.NoEditTriggers)
        self._table.setSelectionBehavior(QTableWidget.SelectRows)
        self._table.setAlternatingRowColors(False)
        layout.addWidget(self._table)

    # ------------------------------------------------------------------ public

    def load_steps(self, steps: list):
        """Populate the table with a list of TraceStep objects."""
        self._steps = steps
        self._current_step = -1
        self._timer.stop()
        self._btn_play.setText("▶ Auto-play")
        self._populate_table()
        self._update_toolbar()

    def clear(self):
        self._steps = []
        self._current_step = -1
        self._table.setRowCount(0)
        self._update_toolbar()

    # ------------------------------------------------------------------ private

    def _populate_table(self):
        self._table.setRowCount(0)
        for i, step in enumerate(self._steps):
            row = self._table.rowCount()
            self._table.insertRow(row)

            stack_str = " | ".join(step.stack) if step.stack else "∅"
            cells = [
                str(i + 1),
                step.action,
                step.symbol,
                stack_str,
                step.lookahead,
                step.rule,
            ]
            for col, text in enumerate(cells):
                item = QTableWidgetItem(text)
                item.setForeground(_COL_FG)
                bg = self._row_colour(step.action)
                item.setBackground(bg)
                self._table.setItem(row, col, item)

    def _row_colour(self, action: str) -> QColor:
        if action == "SHIFT":
            return _COL_SHIFT
        if action == "REDUCE":
            return _COL_REDUCE
        if action == "ACCEPT":
            return _COL_ACCEPT
        return QColor("#2a2a2a")

    def _highlight_row(self, row: int):
        """Highlight *row* in bright yellow and scroll to it."""
        # Clear previous highlight
        for r in range(self._table.rowCount()):
            for c in range(self._table.columnCount()):
                item = self._table.item(r, c)
                if item:
                    item.setBackground(self._row_colour(self._steps[r].action))
                    item.setForeground(_COL_FG)

        # Apply highlight
        if 0 <= row < self._table.rowCount():
            for c in range(self._table.columnCount()):
                item = self._table.item(row, c)
                if item:
                    item.setBackground(QColor("#b8860b"))   # dark goldenrod
                    item.setForeground(QColor("#000000"))
            self._table.scrollToItem(self._table.item(row, 0))

    def _next_step(self):
        if self._current_step < len(self._steps) - 1:
            self._current_step += 1
            self._highlight_row(self._current_step)
            self._update_toolbar()

    def _prev_step(self):
        if self._current_step > 0:
            self._current_step -= 1
            self._highlight_row(self._current_step)
            self._update_toolbar()

    def _reset_step(self):
        self._current_step = -1
        self._timer.stop()
        self._btn_play.setText("▶ Auto-play")
        self._populate_table()   # resets highlight colours
        self._update_toolbar()

    def _toggle_play(self):
        if self._timer.isActive():
            self._timer.stop()
            self._btn_play.setText("▶ Auto-play")
        else:
            self._timer.start(self._speed_slider.value())
            self._btn_play.setText("⏸ Pause")

    def _auto_next(self):
        if self._current_step < len(self._steps) - 1:
            self._next_step()
        else:
            self._timer.stop()
            self._btn_play.setText("▶ Auto-play")

    def _update_toolbar(self):
        total = len(self._steps)
        cur   = self._current_step + 1
        self._step_label.setText(f"Step {cur} / {total}")
        self._btn_prev.setEnabled(self._current_step > 0)
        self._btn_next.setEnabled(self._current_step < total - 1)
        self._btn_play.setEnabled(total > 0)
        self._btn_reset.setEnabled(total > 0)
