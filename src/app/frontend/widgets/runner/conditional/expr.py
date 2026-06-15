from PyQt5.QtWidgets import QTreeWidget, QTreeWidgetItem, QWidget

from .model import ComparisonExpression, Expression, LogicalExpression


class ExpressionNode(QTreeWidget):
    def __init__(self, schema: Expression):
        super().__init__()
        self.setColumnCount(1)


class LogicalNode(QTreeWidgetItem):
    def __init__(self, schema: LogicalExpression):
        super().__init__()


class ComparisionNode(QTreeWidgetItem):
    def __init__(self, schema: ComparisonExpression):
        super().__init__()
        pass
