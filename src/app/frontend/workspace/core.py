from nanoid import generate

from src.app.frontend.events import Node

from .components import WorkspaceMV, WorkspaceSerializer
from .widget import WorkspaceWidget


class WorkspaceComponent(Node):
    def __init__(self):
        super().__init__()
        self.widget = WorkspaceWidget()

        self.wkmv = WorkspaceMV()
        self.serializer = WorkspaceSerializer(self.wkmv)

        self.widget.createBtn.clicked.connect(self.createWorkspace)
        self.widget.exportBtn.clicked.connect(self.workspaceExport)
        self.widget.importBtn.clicked.connect(self.workspaceImport)
        self.wkmv.wkPressed_.connect(self.workspaceFocused)

        self.subscribe("/App/Loaded", self.createRootWorkspace)

    def createRootWorkspace(self, data):
        id = generate()
        self.wkmv.create(id)
        name = "Root"
        self.wkmv.update(id, {"padding": 15, "text": name})
        self.publish(
            "/WS Component/RootWSCreated",
            {
                "text": name,
                "id": id,
            },
        )

    def createWorkspace(self):
        id = generate()
        self.wkmv.create(id)

        name = self.widget.getWorkspaceName()
        data = {"text": name}
        self.wkmv.update(id, data)

        self.publish(
            "/WS Component/WSCreated",
            {
                "text": name,
                "id": id,
            },
        )

    def workspaceFocused(self, id):
        self.publish("/WS Component/WSFocused", {"id": id})

    def workspaceExport(self):
        self.serializer.export()
        self.publish("/WS Component/WSExport")

    def workspaceImport(self):
        self.serializer.restore()
        self.publish("/WS Component/WSImport")
