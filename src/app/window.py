from PyQt5.QtGui import QKeySequence
from PyQt5.QtWidgets import QAction, QApplication, QMainWindow


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        raiseAction = QAction("Bring to Front", self)
        raiseAction.setShortcut(QKeySequence("Ctrl+Shift+M"))
        raiseAction.triggered.connect(self.focus)

        lowerAction = QAction("Send to Back", self)
        lowerAction.setShortcut(QKeySequence("Ctrl+Shift+L"))
        lowerAction.triggered.connect(self.unfocus)

        menu = self.menuBar().addMenu("Window")
        menu.addAction(raiseAction)
        menu.addAction(lowerAction)

    def focus(self):
        self.raise_()
        self.activateWindow()

    def unfocus(self):
        self.lower()

    def closeEvent(self, event):
        QApplication.quit()
