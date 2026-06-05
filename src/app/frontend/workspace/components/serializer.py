import json

from .mv import WorkspaceMV


class WorkspaceSerializer:
    def __init__(self, wkmv: WorkspaceMV):
        self.wkmv = wkmv
        self.path = "workspaceConfig"

    @property
    def controller(self):
        return self.wkmv.controller

    def export(self):
        config = {}
        workspaces = self.controller.workspaces()

        for id in workspaces:
            data = self.controller.readWorkspace(id)
            config[id] = data

        with open(self.path, "w") as f:
            json.dump(config, f, indent=4)

    def restore(self):
        self.wkmv.clear()

        with open(self.path, "r") as f:
            workspaces = json.load(f)

            for id, data in workspaces.items():
                parentID = data.get("parentID")

                self.controller.createWorkspace(id, parentID)
                self.controller.updateWorkspace(id, data)
