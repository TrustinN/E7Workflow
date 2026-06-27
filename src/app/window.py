from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QKeySequence
from PyQt5.QtWidgets import QAction, QApplication, QMainWindow


class MainWindow(QMainWindow):
    requestExport = pyqtSignal()
    requestImport = pyqtSignal()

    def __init__(self):
        super().__init__()
        fileMenu = self.menuBar().addMenu("&File")

        saveAction = QAction("Save", self)
        saveAction.setShortcut(QKeySequence.Save)
        saveAction.triggered.connect(self.requestExport.emit)

        loadAction = QAction("Open...", self)
        loadAction.setShortcut(QKeySequence.Open)
        loadAction.triggered.connect(self.requestImport.emit)

        fileMenu.addAction(loadAction)
        fileMenu.addAction(saveAction)

    def closeEvent(self, event):
        QApplication.quit()
