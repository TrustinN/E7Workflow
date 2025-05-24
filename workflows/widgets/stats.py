from typing import Iterable

import numpy as np
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QApplication, QHBoxLayout, QLabel, QVBoxLayout, QWidget

from assets import BookmarkType, PenguinType, bookmarkIcons, penguinIcons
from workflows.state import GlobalState, StateManager, bookmarkManager, penguinManager


def npToQImage(arr: np.ndarray) -> QImage:
    qimage = None
    height, width, channels = arr.shape
    if channels == 3:  # RGB
        qimage = QImage(arr.data, width, height, QImage.Format_RGB888)
    elif channels == 4:  # RGBA
        qimage = QImage(arr.data, width, height, QImage.Format_RGBA888)
    return qimage


class StatCard(QWidget):
    def __init__(self, title, value, icon: np.ndarray = None):
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
        layout.setContentsMargins(10, 10, 10, 10)

        if icon is not None:
            icon = npToQImage(icon)
            icon = QPixmap(icon).scaled(80, 80, Qt.KeepAspectRatio)
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

    def updateValue(self, value):
        self.valueLabel.setText(str(value))


def makeStatCards(titles, values, iconPaths=None) -> list[StatCard]:
    cards = []
    for i in range(len(titles)):
        iconPath = None
        if iconPaths:
            iconPath = iconPaths[i]
        cards.append(StatCard(titles[i], values[i], iconPath))
    return cards


class StatWindow(QWidget):
    def __init__(self, cards: Iterable[StatCard] = []):
        super().__init__()
        self.cards: dict[str, StatCard] = {}
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        for card in cards:
            self.addCard(card)

    def addCard(self, card: StatCard):
        self.cards[card.title] = card
        self.layout.addWidget(card)

    def addCards(self, cards: list[StatCard]):
        for c in cards:
            self.addCard(c)

    def getCard(self, title: str) -> StatCard:
        return self.cards[title]

    def updateCard(self, title: str, value: any):
        self.getCard(title).updateValue(str(value))


def getStatUpdate(statWidget: StatWindow, manager: StateManager):
    def statUpdate(state: GlobalState):
        wkState = state.getWorkflowState(manager.getScope())
        for key in wkState:
            statWidget.updateCard(key.name, wkState[key])

    return statUpdate


bookmarkCards = {
    bType: StatCard(bType.name, 0, bookmarkIcons[bType]) for bType in BookmarkType
}


def updateBookmarkCards(state: GlobalState):
    for bType in BookmarkType:
        bookmarkCards[bType].updateValue(bookmarkManager.getAmount(bType))


penguinCards = {
    pType: StatCard(pType.name, 0, penguinIcons[pType]) for pType in PenguinType
}


def updatePenguinCards(state: GlobalState):
    for pType in PenguinType:
        penguinCards[pType].updateValue(penguinManager.getAmount(pType))
