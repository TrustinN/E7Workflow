from PyQt5.QtCore import Qt
from PyQt5.QtGui import QKeySequence
from PyQt5.QtWidgets import (
    QAction,
    QApplication,
    QHBoxLayout,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from src.router.routing import Dispatcher

from .actions import ActionRegistry
from .components.action import ActionComponent
from .components.graph import GraphComponent
from .components.runner import RunnerComponent
from .components.script import ScriptComponent
from .components.workspace import WorkspaceComponent
from .events import EventBus
from .serialization import SerializerNode
from .state import Context, ContextManager
from .window import MainWindow


def createAction(name, shortcut, parent) -> QAction:
    action = QAction(name, parent)
    action.setShortcut(shortcut)
    action.setShortcutContext(Qt.ApplicationShortcut)
    return action


class App(QApplication):
    def __init__(self, dispatcher: Dispatcher):
        super().__init__([])

        self.window = MainWindow()
        self.eventBus = EventBus()

        self.context = self._initState()
        self.actions = ActionRegistry()
        self._initActions(self.actions)
        self.components = self._initComponents(self.context, self.actions, dispatcher)
        self._initLayout()

        self._initEvents(self.eventBus)
        self.eventBus.handlePublish("/App/Loaded")

    def _initState(self) -> Context:
        context = Context()
        self.contextManager = ContextManager(context)
        return context

    def _initActions(self, actions: ActionRegistry):
        actionMap = {
            "Create Workspace": (QKeySequence.New, "/Workspace/Create/Request"),
            "Delete Workspace": ("Meta+Backspace", "/Workspace/Delete/Request"),
            "Set Edge Start": ("1", "/Graph/Edge/SetStart/Request"),
            "Set Edge End": ("2", "/Graph/Edge/SetEnd/Request"),
            "Create Edge": ("E", "/Graph/Edge/Create/Request"),
            "Delete Edge": ("Backspace", "/Graph/Edge/Delete/Request"),
            "Set Action": ("3", "/Runner/Action/Set/Request"),
            "Unset Action": ("4", "/Runner/Action/Unset/Request"),
            "Set Script": ("5", "/Runner/Script/Set/Request"),
            "Unset Script": ("6", "/Runner/Script/Unset/Request"),
            "Set Entry": ("Return", "/Runner/Entry/Set/Request"),
            "Execute": ("Ctrl+R", "/Runner/Execute/Request"),
            "Save": (QKeySequence.Save, "/App/Export/Request"),
            "Open": (QKeySequence.Open, "/App/Import/Request"),
        }

        for name, (shortcut, event) in actionMap.items():
            action = createAction(name, shortcut, self.window)
            self.window.addAction(action)
            action.triggered.connect(lambda _, e=event: self.eventBus.handlePublish(e))
            actions.register(name, action)

    def _initComponents(
        self, context: Context, actions: ActionRegistry, dispatcher: Dispatcher
    ):
        self.wkCpt = WorkspaceComponent(context, actions, dispatcher)
        self.graphCpt = GraphComponent(context, actions, dispatcher)
        self.actionCpt = ActionComponent(context, dispatcher)
        self.scriptCpt = ScriptComponent(context, dispatcher)
        self.runnerCpt = RunnerComponent(context, actions, dispatcher)
        self.serialCpt = SerializerNode(context)

        return [
            self.wkCpt,
            self.graphCpt,
            self.actionCpt,
            self.scriptCpt,
            self.runnerCpt,
            self.serialCpt,
        ]

    def _initLayout(self):
        self.widget = QWidget()

        self.layout = QHBoxLayout(self.widget)
        self.layoutLeft = QVBoxLayout()
        self.layoutMid = QVBoxLayout()
        self.layoutRight = QVBoxLayout()
        self.layout.addLayout(self.layoutLeft)
        self.layout.addLayout(self.layoutMid)
        self.layout.addLayout(self.layoutRight)

        self.window.setCentralWidget(self.widget)
        self.window.show()

        self.layoutLeft.addStretch()

        self.layoutMid.addWidget(self.graphCpt.display)
        self.layoutMid.addStretch()

        self.tabs = QTabWidget()
        self.tabs.addTab(self.wkCpt.editor, "Workspace")
        self.tabs.addTab(self.graphCpt.editor, "Graph")
        self.tabs.addTab(self.actionCpt.editor, "Actions")
        self.tabs.addTab(self.scriptCpt.editor, "Scripts")

        self.layoutRight.addWidget(self.runnerCpt.editor)
        self.layoutRight.addWidget(self.tabs)
        self.layoutRight.addStretch()

    def _initEvents(self, eventBus: EventBus):
        self.eventBus.registerNode(self.contextManager)
        self.eventBus.registerNodes(self.components)
