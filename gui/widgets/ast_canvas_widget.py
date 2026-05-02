"""
ast_canvas_widget.py
--------------------
A QGraphicsView that renders the AST as a proper node-and-edge graph.

Layout algorithm
~~~~~~~~~~~~~~~~
1. Walk the AST to compute the *width* of each subtree (number of leaf
   positions it needs).
2. In a second pass assign x/y coordinates top-down, centring each parent
   over its children.
3. Draw edges first (so they are behind nodes), then draw rounded-rect nodes
   with the node-type label and an optional value label.

The widget exposes a single public method:

    canvas.display_ast(root_ast_node)

which clears the scene and redraws from scratch.
"""

from PyQt5.QtWidgets import (
    QGraphicsView, QGraphicsScene, QGraphicsRectItem,
    QGraphicsTextItem, QGraphicsLineItem, QGraphicsEllipseItem,
    QGraphicsItem, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QSlider, QLabel
)
from PyQt5.QtCore import Qt, QRectF, QPointF
from PyQt5.QtGui import (
    QColor, QPen, QBrush, QFont, QPainter, QWheelEvent
)

from src.ast_nodes import (
    ASTNode, Program, Declaration, Assignment, IfStatement,
    WhileStatement, BinaryExpression, UnaryExpression,
    Identifier, NumberLiteral, StringLiteral, EmptyStatement
)

# ── Layout constants ──────────────────────────────────────────────────────────
_H_GAP   = 30    # horizontal gap between sibling subtrees
_V_GAP   = 70    # vertical gap between levels
_NODE_W  = 130   # node rectangle width
_NODE_H  = 44    # node rectangle height (single-line)
_NODE_H2 = 60    # node rectangle height (two-line, with value)

# ── Colour palette (node type → background hex) ───────────────────────────────
_BG = {
    Program:          "#1a3a5c",
    Declaration:      "#4a235a",
    Assignment:       "#145a32",
    IfStatement:      "#7d5200",
    WhileStatement:   "#7d3800",
    BinaryExpression: "#7b241c",
    UnaryExpression:  "#6e2c2c",
    Identifier:       "#1a5e20",
    NumberLiteral:    "#0d3b7c",
    StringLiteral:    "#4a0e6e",
    EmptyStatement:   "#3d3d3d",
}
_FG = "#f0f0f0"


# ── Helpers ───────────────────────────────────────────────────────────────────

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


def _children(node):
    """Return the direct ASTNode children of *node* in display order."""
    result = []
    for attr in _CHILD_ATTRS.get(type(node), []):
        val = getattr(node, attr, None)
        if val is None:
            continue
        if isinstance(val, ASTNode):
            result.append(val)
        elif isinstance(val, list):
            result.extend(c for c in val if isinstance(c, ASTNode))
    return result


def _node_texts(node):
    """Return (primary_label, secondary_label_or_None) for a node."""
    t = type(node).__name__
    if isinstance(node, Declaration):
        return t, f"type: {node.var_type}"
    if isinstance(node, Identifier):
        return t, f"'{node.name}'"
    if isinstance(node, NumberLiteral):
        return t, str(node.value)
    if isinstance(node, StringLiteral):
        return t, f'"{node.value}"'
    if isinstance(node, BinaryExpression):
        return t, f"op: '{node.operator}'"
    if isinstance(node, UnaryExpression):
        return t, f"op: '{node.operator}'"
    if isinstance(node, IfStatement):
        return t, "with else" if node.else_block else "no else"
    return t, None


# ── Layout computation ────────────────────────────────────────────────────────

class _LayoutNode:
    """Lightweight wrapper used during layout."""
    __slots__ = ('ast', 'children', 'width', 'x', 'y')

    def __init__(self, ast_node):
        self.ast = ast_node
        self.children: list['_LayoutNode'] = []
        self.width = 0
        self.x = 0.0
        self.y = 0.0


def _build_layout_tree(ast_node):
    """Recursively build a _LayoutNode tree from the AST."""
    ln = _LayoutNode(ast_node)
    for child in _children(ast_node):
        ln.children.append(_build_layout_tree(child))
    return ln


def _compute_widths(ln: _LayoutNode):
    """Bottom-up: set each node's width to the total width of its subtree."""
    if not ln.children:
        ln.width = _NODE_W
        return
    for child in ln.children:
        _compute_widths(child)
    ln.width = (sum(c.width for c in ln.children)
                + _H_GAP * (len(ln.children) - 1))


def _assign_positions(ln: _LayoutNode, x_left: float, y: float):
    """Top-down: assign (x, y) so the node is centred over its children."""
    ln.y = y
    if not ln.children:
        ln.x = x_left + _NODE_W / 2
        return
    cursor = x_left
    for child in ln.children:
        _assign_positions(child, cursor, y + _NODE_H2 + _V_GAP)
        cursor += child.width + _H_GAP
    # Centre this node over the span of its children
    leftmost  = ln.children[0].x
    rightmost = ln.children[-1].x
    ln.x = (leftmost + rightmost) / 2


# ── Graphics items ────────────────────────────────────────────────────────────

class _NodeItem(QGraphicsItem):
    """A single node drawn as a rounded rectangle with label(s)."""

    def __init__(self, ln: _LayoutNode):
        super().__init__()
        self.ln = ln
        primary, secondary = _node_texts(ln.ast)
        self.primary   = primary
        self.secondary = secondary
        self.h = _NODE_H2 if secondary else _NODE_H
        self.bg = QColor(_BG.get(type(ln.ast), "#333333"))

        self.setPos(ln.x - _NODE_W / 2, ln.y)
        self.setToolTip(f"{primary}" + (f"\n{secondary}" if secondary else ""))

    def boundingRect(self):
        return QRectF(0, 0, _NODE_W, self.h)

    def paint(self, painter, option, widget=None):
        painter.setRenderHint(QPainter.Antialiasing)

        # Background
        painter.setBrush(QBrush(self.bg))
        painter.setPen(QPen(QColor("#ffffff"), 0.8, Qt.SolidLine))
        painter.drawRoundedRect(0, 0, _NODE_W, self.h, 8, 8)

        # Primary label
        font = QFont("Consolas", 9, QFont.Bold)
        painter.setFont(font)
        painter.setPen(QColor(_FG))
        if self.secondary:
            painter.drawText(QRectF(4, 4, _NODE_W - 8, self.h / 2 - 2),
                             Qt.AlignCenter, self.primary)
            # Secondary label
            font2 = QFont("Consolas", 8)
            painter.setFont(font2)
            painter.setPen(QColor("#cccccc"))
            painter.drawText(QRectF(4, self.h / 2, _NODE_W - 8, self.h / 2 - 4),
                             Qt.AlignCenter, self.secondary)
        else:
            painter.drawText(QRectF(4, 0, _NODE_W - 8, self.h),
                             Qt.AlignCenter, self.primary)


# ── Main widget ───────────────────────────────────────────────────────────────

class ASTCanvasWidget(QWidget):
    """
    A zoomable / pannable canvas that renders the AST as a node-edge graph.

    Usage:
        canvas = ASTCanvasWidget()
        canvas.display_ast(ast_root)
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self._scene = QGraphicsScene(self)
        self._view  = _ZoomableView(self._scene, self)

        # Toolbar
        btn_fit    = QPushButton("Fit view")
        btn_zoom_in  = QPushButton("+")
        btn_zoom_out = QPushButton("−")
        btn_fit.clicked.connect(self._fit)
        btn_zoom_in.clicked.connect(lambda: self._view.scale(1.2, 1.2))
        btn_zoom_out.clicked.connect(lambda: self._view.scale(1/1.2, 1/1.2))
        for btn in (btn_fit, btn_zoom_in, btn_zoom_out):
            btn.setFixedHeight(26)
            btn.setFixedWidth(70)

        toolbar = QHBoxLayout()
        toolbar.addWidget(btn_zoom_in)
        toolbar.addWidget(btn_zoom_out)
        toolbar.addWidget(btn_fit)
        toolbar.addStretch()
        toolbar.addWidget(QLabel("Drag to pan  •  Scroll to zoom"))

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addLayout(toolbar)
        layout.addWidget(self._view)

    # ------------------------------------------------------------------

    def display_ast(self, root):
        """Clear the canvas and draw the AST rooted at *root*."""
        self._scene.clear()
        if root is None:
            return

        ln = _build_layout_tree(root)
        _compute_widths(ln)
        _assign_positions(ln, 0, 0)

        self._draw_edges(ln)
        self._draw_nodes(ln)

        self._scene.setSceneRect(self._scene.itemsBoundingRect().adjusted(-20, -20, 20, 20))
        self._fit()

    def _draw_nodes(self, ln: _LayoutNode):
        item = _NodeItem(ln)
        self._scene.addItem(item)
        for child in ln.children:
            self._draw_nodes(child)

    def _draw_edges(self, ln: _LayoutNode):
        pen = QPen(QColor("#888888"), 1.2, Qt.SolidLine)
        pen.setCapStyle(Qt.RoundCap)
        for child in ln.children:
            # From bottom-centre of parent to top-centre of child
            x1 = ln.x
            y1 = ln.y + (_NODE_H2 if _node_texts(ln.ast)[1] else _NODE_H)
            x2 = child.x
            y2 = child.y
            line = QGraphicsLineItem(x1, y1, x2, y2)
            line.setPen(pen)
            self._scene.addItem(line)
            self._draw_edges(child)

    def _fit(self):
        self._view.fitInView(self._scene.sceneRect(), Qt.KeepAspectRatio)


class _ZoomableView(QGraphicsView):
    """QGraphicsView with mouse-wheel zoom and middle-button pan."""

    def __init__(self, scene, parent=None):
        super().__init__(scene, parent)
        self.setRenderHint(QPainter.Antialiasing)
        self.setDragMode(QGraphicsView.ScrollHandDrag)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.AnchorUnderMouse)
        self.setBackgroundBrush(QBrush(QColor("#1e1e1e")))
        self.setFrameShape(QGraphicsView.NoFrame)

    def wheelEvent(self, event: QWheelEvent):
        factor = 1.15 if event.angleDelta().y() > 0 else 1 / 1.15
        self.scale(factor, factor)
