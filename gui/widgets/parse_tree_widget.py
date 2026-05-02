from PyQt5.QtWidgets import QTreeWidget, QTreeWidgetItem, QHeaderView
from PyQt5.QtGui import QColor
from src.ast_nodes import (
    ASTNode, Program, Declaration, Assignment, IfStatement, WhileStatement,
    BinaryExpression, UnaryExpression, Identifier, NumberLiteral,
    StringLiteral, EmptyStatement
)


# Maps each AST node class to the ordered list of child attributes to display.
# Using an explicit whitelist avoids the double-traversal bug that appeared when
# the widget walked both named attributes AND dir(node) simultaneously.
_CHILD_ATTRS = {
    Program:          ['statements'],
    Declaration:      ['identifier'],
    Assignment:       ['identifier', 'expression'],
    IfStatement:      ['condition', 'then_block', 'else_block'],
    WhileStatement:   ['condition', 'body'],
    BinaryExpression: ['left', 'right'],
    UnaryExpression:  ['operand'],
    Identifier:       [],
    NumberLiteral:    [],
    StringLiteral:    [],
    EmptyStatement:   [],
}


def _node_label(node):
    """Return a short human-readable value string for a node."""
    if isinstance(node, Declaration):
        return f"type={node.var_type}"
    if isinstance(node, Assignment):
        return f"var={node.identifier.name}"
    if isinstance(node, BinaryExpression):
        return f"op='{node.operator}'"
    if isinstance(node, UnaryExpression):
        return f"op='{node.operator}'"
    if isinstance(node, Identifier):
        return f"name={node.name}"
    if isinstance(node, NumberLiteral):
        return f"value={node.value}"
    if isinstance(node, StringLiteral):
        return f'value="{node.value}"'
    if isinstance(node, IfStatement):
        has_else = "with else" if node.else_block else "no else"
        return has_else
    if isinstance(node, WhileStatement):
        return f"body={len(node.body)} stmt(s)"
    if isinstance(node, Program):
        return f"{len(node.statements)} stmt(s)"
    return ""


# Colour-coding by node family
_NODE_COLOURS = {
    Program:          "#1e6b9e",   # blue
    Declaration:      "#7c4dba",   # purple
    Assignment:       "#1a7a4a",   # green
    IfStatement:      "#c07a00",   # amber
    WhileStatement:   "#b85c00",   # orange
    BinaryExpression: "#c0392b",   # red
    UnaryExpression:  "#a93226",
    Identifier:       "#2e7d32",
    NumberLiteral:    "#1565c0",
    StringLiteral:    "#6a1b9a",
    EmptyStatement:   "#808080",
}


class ParseTreeWidget(QTreeWidget):
    def __init__(self):
        super().__init__()
        self.setHeaderLabels(["Node type", "Value"])
        self.setAlternatingRowColors(True)
        self.header().setSectionResizeMode(0, QHeaderView.Interactive)
        self.header().setSectionResizeMode(1, QHeaderView.Interactive)
        self.header().setStretchLastSection(True)
        self.setColumnWidth(0, 220)

    # ------------------------------------------------------------------

    def build_tree(self, node, parent=None):
        if node is None:
            return

        node_type = type(node)
        node_type_name = node_type.__name__

        # Create the tree item
        item = QTreeWidgetItem()
        item.setText(0, node_type_name)
        item.setText(1, _node_label(node))

        # Apply colour
        colour = _NODE_COLOURS.get(node_type, "#444444")
        item.setForeground(0, QColor(colour))

        if parent is None:
            self.addTopLevelItem(item)
        else:
            parent.addChild(item)

        # Recurse only over the whitelisted child attributes
        child_attrs = _CHILD_ATTRS.get(node_type, [])
        for attr in child_attrs:
            value = getattr(node, attr, None)
            if value is None:
                continue
            if isinstance(value, ASTNode):
                self.build_tree(value, item)
            elif isinstance(value, list):
                for child in value:
                    if isinstance(child, ASTNode):
                        self.build_tree(child, item)

        item.setExpanded(True)
