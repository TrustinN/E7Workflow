from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication, QHBoxLayout, QLabel, QVBoxLayout, QWidget

from app import GlobalState, WorkflowRunner, WorkflowWindow, Workspace


class StatCard(QWidget):
    def __init__(self, title, value, iconPath=None):
        super().__init__()

        textLayout = QVBoxLayout()
        textWidget = QWidget()
        textWidget.setLayout(textLayout)

        self.title = title
        self.value = value
        self.titleLabel = QLabel(self.title)
        self.valueLabel = QLabel(str(self.value))
        self.titleLabel.setStyleSheet("font-size: 16px; color: gray;")
        self.valueLabel.setStyleSheet("font-size: 24px; font-weight: bold;")

        textLayout.addWidget(self.titleLabel)
        textLayout.addWidget(self.valueLabel)

        layout = QHBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        layout.setContentsMargins(10, 10, 10, 10)  # Padding inside the card

        if iconPath:
            icon = QPixmap(iconPath).scaled(80, 80, Qt.KeepAspectRatio)
            iconLabel = QLabel()
            iconLabel.setPixmap(icon)
            iconLabel.setStyleSheet(
                """
                border: 2px solid #555555;
                border-radius: 10px;
                padding: 5px;
            """
            )
            layout.addWidget(iconLabel)

        layout.addWidget(textWidget)

        self.setLayout(layout)


def makeStatCards(titles, values, iconPaths=None):
    cards = []
    for i in range(len(titles)):
        iconPath = None
        if iconPaths:
            iconPath = iconPaths[i]
        cards.append(StatCard(titles[i], values[i], iconPath))
    return cards


class StatWindow(QWidget):
    def __init__(self, cards=[]):
        super().__init__()
        self.cards = {}
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        for card in cards:
            self.addCard(card)

    def addCard(self, card):
        self.cards[card.title] = card
        self.layout.addWidget(card)

    def getCard(self, title):
        return self.cards[title]

    def updateCard(self, title, value):
        self.getCard(title).valueLabel.setText(str(value))


def getStatUpdate(statWidget: StatWindow, wkspace: Workspace):
    def statUpdate(state: GlobalState):
        wkState = state.getWorkflowState(wkspace.name)
        stats = wkState.getField("stats")
        for key in stats:
            statWidget.updateCard(key, stats[key])
        QApplication.processEvents()

    return statUpdate


def addStatWindow(
    window: WorkflowWindow,
    runner: WorkflowRunner,
    statWkspace: Workspace,
    statWindow: StatWindow,
):
    window.addWidget(statWindow)
    runner.stepFinished.connect(getStatUpdate(statWindow, statWkspace))
