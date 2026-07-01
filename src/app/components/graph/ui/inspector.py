from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget

from src.app.components.graph.model import GraphModel
from src.app.state import Context, Selection, SelectionType


class Inspector(QWidget):
    def __init__(self, context: Context, model: GraphModel):
        super().__init__()
        self.layout = QVBoxLayout(self)

        self.context = context
        self.model = model

        self.model.modelCleared.connect(self.clearLayout)
        self.context.selectionModel.selected_.connect(self.onSelectionChanged)

    def clearLayout(self, layout=None):
        if layout is None:
            layout = self.layout

        while layout.count():
            item = layout.takeAt(0)

            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
                continue

            child = item.layout()
            if child is not None:
                self.clearLayout(child)

    def onSelectionChanged(self, selection: Selection):
        if not (selection.id and selection.type == SelectionType.WORKSPACE):
            self.setDisabled(True)
            return

        self.setDisabled(False)
        self.clearLayout()

        edges = self.model.getNodeEdges(selection.id)
        for edgeID in edges:
            edge = self.model.getEdge(edgeID)
            source = self.model.getNode(edge.source)
            target = self.model.getNode(edge.target)

            edgeBtn = QPushButton("->")
            edgeBtn.clicked.connect(
                lambda _, eID=edgeID: self.context.selectionModel.setSelected(
                    eID, SelectionType.EDGE
                )
            )

            sourceLabel = QLabel(f'"{source.name}"')
            targetLabel = QLabel(f'"{target.name}"')

            sourceLabel.setAlignment(Qt.AlignCenter)
            targetLabel.setAlignment(Qt.AlignCenter)

            row = QHBoxLayout()

            row.addWidget(sourceLabel, 1)
            row.addWidget(edgeBtn)
            row.addWidget(targetLabel, 1)

            self.layout.addLayout(row)
