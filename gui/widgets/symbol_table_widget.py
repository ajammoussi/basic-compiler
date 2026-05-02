from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem, QHeaderView
from PyQt5.QtGui import QColor


class SymbolTableWidget(QTableWidget):
    def __init__(self):
        super().__init__()
        self.setColumnCount(5)
        self.setHorizontalHeaderLabels(["Scope", "Name", "Type", "Line", "Column"])
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        self.horizontalHeader().setStretchLastSection(True)
        self.setAlternatingRowColors(True)
        self.setEditTriggers(QTableWidget.NoEditTriggers)
        self.setSelectionBehavior(QTableWidget.SelectRows)

    def update_from_symbol_table(self, symbol_table):
        self.setRowCount(0)

        type_colours = {
            'int':    QColor("#1565c0"),
            'string': QColor("#6a1b9a"),
        }

        for scope_idx, scope in enumerate(symbol_table.scopes):
            for name, info in scope.items():
                row = self.rowCount()
                self.insertRow(row)

                self.setItem(row, 0, QTableWidgetItem(f"Scope {scope_idx}"))
                self.setItem(row, 1, QTableWidgetItem(name))

                type_item = QTableWidgetItem(info['type'])
                colour = type_colours.get(info['type'])
                if colour:
                    type_item.setForeground(colour)
                self.setItem(row, 2, type_item)

                self.setItem(row, 3, QTableWidgetItem(str(info.get('line', ''))))
                self.setItem(row, 4, QTableWidgetItem(str(info.get('column', ''))))
