from PyQt5.QtWidgets import QApplication, QHBoxLayout, QMainWindow, QPushButton, QWidget

from src.router.routing import Dispatcher

from .graph import GraphWidget
from .workspace import WorkspaceWidget

DATA_DISPLAY = "Data Display"


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

    def closeEvent(self, event):
        QApplication.quit()


class App(QApplication):
    def __init__(self, dispatcher: Dispatcher):
        super().__init__([])

        self.window = MainWindow()
        self.widget = QWidget()
        self.layout = QHBoxLayout()
        self.widget.setLayout(self.layout)
        self.window.setCentralWidget(self.widget)
        self.window.show()

        self.graphWidget = GraphWidget(dispatcher)
        self.workspaceWidget = WorkspaceWidget(dispatcher)

        self.importBtn = QPushButton("Import")
        self.exportBtn = QPushButton("Export")

        self.layout.addWidget(self.graphWidget)
        self.layout.addWidget(self.workspaceWidget)
