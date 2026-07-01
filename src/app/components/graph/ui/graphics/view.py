from PyQt5.QtWidgets import QGraphicsView, QSizePolicy


class GraphView(QGraphicsView):

    def __init__(self, scene, parent=None):
        super().__init__(scene, parent=None)

        self.setMinimumWidth(450)
        self.setSizePolicy(
            QSizePolicy.Expanding,
            QSizePolicy.Expanding,
        )

    def resizeEvent(self, event):
        super().resizeEvent(event)

        self.scene().setSceneRect(
            0,
            0,
            self.viewport().width(),
            self.viewport().height(),
        )
