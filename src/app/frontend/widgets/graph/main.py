from PyQt5.QtWidgets import QVBoxLayout, QWidget

from src.app.frontend.events import Node
from src.app.frontend.state import Context, Document

from .builders import GraphFullViewBuilder, GraphMiniViewBuilder
from .controllers import GraphFullViewController, GraphMiniViewController
from .layout import GraphLayoutSync
from .views import GraphMultiView, GraphSingleView


class GraphComponent(Node):

    def __init__(self, context: Context, document: Document):
        super().__init__()
        self.context = context
        self.document = document

        self.miniView = GraphMultiView()
        self.miniViewBuilder = GraphMiniViewBuilder(self.context, self.miniView)
        self.miniViewLayout = GraphLayoutSync(self.document.miniView, self.miniView)
        self.miniViewController = GraphMiniViewController(self.context, self.miniView)

        self.fullView = GraphSingleView()
        self.fullViewBuilder = GraphFullViewBuilder(self.context, self.fullView)
        self.fullViewLayout = GraphLayoutSync(self.document.fullView, self.fullView)
        self.fullViewController = GraphFullViewController(self.context, self.fullView)

        self.widget = QWidget()
        self.layout = QVBoxLayout()
        self.widget.setLayout(self.layout)
        self.layout.addWidget(self.miniView)
        self.layout.addWidget(self.fullView)

        self.subscribe("/Graph/Root/Requested", self.createRoot)
        self.subscribe("/Graph/Node/Requested", self.createNode)
        self.subscribe("/Graph/Edge/Requested", self.createEdge)
        self.subscribe("/App/Reset", self.resetState)
        self.subscribe("/App/Import", self.loadState)

    def createRoot(self, data):
        id = data["id"]
        self.miniViewBuilder.createRoot(id)
        self.fullViewBuilder.createGraph(id)
        self.publish("/Graph/Root/Created", data)

    def createNode(self, data):
        id = data["id"]
        self.miniViewBuilder.createNode(id)
        self.fullViewBuilder.createNode(id)
        self.publish("/Graph/Node/Created", data)

    def createEdge(self, data):
        id = data["id"]
        self.miniViewBuilder.createEdge(id)
        self.fullViewBuilder.createEdge(id)
        self.publish("/Graph/Edge/Created", data)

    def resetState(self, data):
        self.miniViewLayout.resetState()
        self.miniViewController.resetState()

        self.fullViewLayout.resetState()
        self.fullViewController.resetState()

    def loadState(self, data):
        self.miniViewLayout.freezeLayout()
        self.miniViewBuilder.buildAll()
        self.miniViewLayout.rerenderView()
        self.miniViewLayout.unfreezeLayout()

        self.fullViewLayout.freezeLayout()
        self.fullViewBuilder.buildAll()
        self.fullViewLayout.rerenderView()
        self.fullViewLayout.unfreezeLayout()
