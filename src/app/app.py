from PyQt5.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from src.router.routing import Dispatcher

from .graph import GraphWidget

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
        self.col2Layout = QVBoxLayout()
        self.col3Layout = QVBoxLayout()
        self.widget.setLayout(self.layout)
        self.window.setCentralWidget(self.widget)
        self.window.show()

        self.graphWidget = GraphWidget(dispatcher)

        self.importBtn = QPushButton("Import")
        self.exportBtn = QPushButton("Export")

        self.layout.addWidget(self.graphWidget)
