from PyQt5.QtWidgets import QTreeWidget, QTreeWidgetItem, QHeaderView
from src.ast_nodes import ASTNode

class ParseTreeWidget(QTreeWidget):
    def __init__(self):
        super().__init__()
        self.setHeaderLabels(["Node", "Value"])
        self.setAlternatingRowColors(True)
        self.setStyleSheet("")
        self.header().setSectionResizeMode(QHeaderView.Interactive)
        self.header().setStretchLastSection(True)

    def build_tree(self, node, parent=None):
        if node is None:
            return

        node_type = type(node).__name__
        item = QTreeWidgetItem(parent)

        if parent is None:
            self.addTopLevelItem(item)

        item.setText(0, node_type)

        if hasattr(node, 'var_type'):
            item.setText(1, f"type: {node.var_type}")
        elif hasattr(node, 'name'):
            item.setText(1, f"name: {node.name}")
        elif hasattr(node, 'value'):
            item.setText(1, f"value: {node.value}")
        elif hasattr(node, 'operator'):
            item.setText(1, f"op: {node.operator}")
        elif hasattr(node, 'statements'):
            item.setText(1, f"statements: {len(node.statements)}")
        elif hasattr(node, 'identifier'):
            item.setText(1, f"var: {node.identifier.name}")
        elif hasattr(node, 'expression'):
            item.setText(1, f"expr: {type(node.expression).__name__}")
        elif hasattr(node, 'condition'):
            item.setText(1, f"cond: {type(node.condition).__name__}")
        elif hasattr(node, 'then_block'):
            item.setText(1, f"then: {len(node.then_block)} stmts")
        elif hasattr(node, 'else_block'):
            item.setText(1, f"else: {len(node.else_block) if node.else_block else 0} stmts")
        elif hasattr(node, 'body'):
            item.setText(1, f"body: {len(node.body)} stmts")
        elif hasattr(node, 'left'):
            item.setText(1, f"left: {type(node.left).__name__}, right: {type(node.right).__name__}")
        elif hasattr(node, 'operand'):
            item.setText(1, f"operand: {type(node.operand).__name__}")

        for attr_name in dir(node):
            if attr_name.startswith('_'):
                continue
            attr_value = getattr(node, attr_name)
            if callable(attr_value):
                continue
            if isinstance(attr_value, ASTNode):
                self.build_tree(attr_value, item)
            elif isinstance(attr_value, list) and attr_value:
                for child in attr_value:
                    if isinstance(child, ASTNode):
                        self.build_tree(child, item)

        item.setExpanded(True)
