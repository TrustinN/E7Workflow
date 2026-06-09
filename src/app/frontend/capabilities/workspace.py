from src.app.frontend.events import Node


class WorkspaceCapability(Node):
    def __init__(self):
        super().__init__()

    def createWorkspace(self, name):
        self.publish("/Workspace/CreateRequested", {"name": name})
