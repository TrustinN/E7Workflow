from .controller import WorkspaceController
from .repository import WorkspaceRepository


class WorkspaceBuilder:
    def __init__(
        self,
        controller: WorkspaceController,
        repository: WorkspaceRepository,
    ):
        self.repository = repository
        self.controller = controller

    def create(self, parentID=None):
        id = self.repository.createWorkspace()
        self.controller.createWorkspace(id, parentID)

        return id

    def update(self, id, data):
        self.repository.updateWorkspace(id, data)
        self.controller.updateWorkspace(id, data)
