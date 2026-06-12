from nanoid import generate

from src.app.frontend.events import Node


class WorkspaceCapability(Node):
    def __init__(self):
        super().__init__()

        self.subscribe("/App/Loaded", self.createRootWorkspace)

    def createRootWorkspace(self, data):
        id = generate()
        name = "Root"
        data = {
            "text": name,
            "id": id,
        }
        self.publish("/Workspace/CreateRootRequested", data)

    def createWorkspace(self, name):
        id = generate()
        data = {
            "text": name,
            "id": id,
        }
        self.publish("/Workspace/CreateRequested", data)
