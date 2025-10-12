from src.app.frontend.components import Capability, Component, JsonFormatter

from ..widget import GraphWidget
from .controller import GraphController
from .repository import GraphRepository
from .view import GraphView


class GraphUIComponent(Component):
    CREATE_GRAPH = "Create Graph"
    CREATE_NODE = "Create Node"
    CREATE_EDGE = "Create Edge"

    UPDATE_NODE = "Update Node"

    SET_SCENE = "Set Scene"

    def __init__(self, graphUI: "GraphUI"):
        super().__init__()
        self.gui = graphUI

        createGraphFmt = JsonFormatter(["sceneID"])
        createNodeFmt = JsonFormatter(["nodeID"])

        createGraphCapability = Capability(self.createGraph, reformat=createGraphFmt)
        createNodeCapability = Capability(self.createNode, reformat=createNodeFmt)
        createEdgeCapability = Capability(self.createEdge)
        updateNodeCapability = Capability(self.updateNode)

        setSceneCapability = Capability(self.setScene)

        self.registerCapability(self.CREATE_GRAPH, createGraphCapability)
        self.registerCapability(self.CREATE_NODE, createNodeCapability)
        self.registerCapability(self.CREATE_EDGE, createEdgeCapability)
        self.registerCapability(self.UPDATE_NODE, updateNodeCapability)
        self.registerCapability(self.SET_SCENE, setSceneCapability)

    def createGraph(self, data):
        return self.gui.createGraph()

    def createNode(self, data):
        graphID = data.get("activeScene")
        return self.gui.createNode(graphID)

    def updateNode(self, data):
        wksID = data.get("id")
        text = data.get("text")

        sceneID = data.get("workspaceViewMapping").get(wksID)
        nodeID = data.get("workspaceNodeMapping").get(wksID)

        nodeData = {"displayText": text}

        if nodeID:
            parentScene = data.get("sceneParents").get(sceneID)
            return self.gui.updateNode(parentScene, nodeID, nodeData)

    def createEdge(self, data):
        graphID = data.get("activeScene")
        if graphID:
            return self.gui.createEdge(graphID)

    def setScene(self, data):
        wksID = data.get("id")

        mapping = data.get("workspaceViewMapping")
        graphID = mapping.get(wksID)
        return self.gui.setScene(graphID)


class GraphUI:
    def __init__(self, widget: GraphWidget, repository: GraphRepository):
        self.widget = widget
        self.repository = repository

        self.controllers = {}
        self.views = {}

    def controller(self, graphID):
        return self.controllers[graphID]

    def setScene(self, graphID):
        view = self.views[graphID]
        self.widget.setScene(view)

    def createController(self, graphID):
        view = GraphView()
        controller = GraphController(view)
        self.controllers[graphID] = controller
        self.views[graphID] = view
        return controller, view

    def createGraph(self):
        sceneID = self.repository.createGraph()
        _, view = self.createController(sceneID)

        if self.widget.scene is None:
            self.widget.setScene(view)

        return sceneID

    def createNode(self, graphID):
        nodeID = self.repository.createNode(graphID)

        controller = self.controller(graphID)
        controller.createNode(nodeID)

        return nodeID

    def updateNode(self, graphID, nodeID, data):
        controller = self.controller(graphID)
        controller.updateNode(nodeID, data)

    def createEdge(self, graphID):
        controller = self.controller(graphID)
        if not controller.canCreateEdge():
            return

        edgeID = self.repository.createEdge(graphID)
        ids = controller.createEdge(edgeID)
        if ids:
            self.repository.updateEdge(graphID, edgeID, {"id1": ids[0], "id2": ids[1]})

    def clear(self):
        for view in self.views.values():
            view.deleteLater()

        self.views.clear()
        self.controllers.clear()
