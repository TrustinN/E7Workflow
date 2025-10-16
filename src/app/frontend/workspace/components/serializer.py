from src.app.frontend.components import Capability, Component, Serializer
from src.app.frontend.events import EventLog

from ..events import WKEvents
from .gui import WorkspaceUI


class WorkspaceSerializerComponent(Component):
    IMPORT = "Import"
    EXPORT = "Export"

    def __init__(self, serializer: Serializer, eventLog: EventLog):
        super().__init__()
        self.serializer = serializer
        self.eventLog = eventLog

        importCapability = Capability(self.restore)
        exportCapability = Capability(self.export)

        self.registerCapability(self.IMPORT, importCapability)
        self.registerCapability(self.EXPORT, exportCapability)

    def export(self):
        self.serializer.export()
        self.eventLog.processEvent(WKEvents.WK_EXPORTED)

    def restore(self):
        self.serializer.restore()
        self.eventLog.processEvent(WKEvents.WK_IMPORTED)


class WorkspaceSerializer:
    def __init__(
        self,
        wkUI: WorkspaceUI,
    ):
        self.repository = wkUI.repository
        self.gui = wkUI

    @property
    def controller(self):
        return self.gui.controller

    def export(self):
        workspaces = self.repository.getAllWorkspaces()

        for id in workspaces:
            config = self.controller.readWorkspace(id)
            self.repository.updateWorkspace(id, config)

        self.repository.exportWorkspaces()

    def restore(self):
        self.gui.clear()
        self.repository.importWorkspaces()

        workspaces = self.repository.getAllWorkspaces()

        for id, data in workspaces.items():
            parentID = data.get("parentID")

            self.controller.createWorkspace(id, parentID)
            self.controller.updateWorkspace(id, data)


# class WorkspaceSerializer:
#     def __init__(
#         self,
#         controller: WorkspaceController,
#         repository: WorkspaceRepository,
#         eventLog: EventLog,
#     ):
#         self.repository = repository
#         self.controller = controller
#         self.eventLog = eventLog
#
#     def export(self):
#         workspaces = self.repository.getAllWorkspaces()
#
#         for id in workspaces:
#             config = self.controller.readWorkspace(id)
#             self.repository.updateWorkspace(id, config)
#
#         self.repository.exportWorkspaces()
#         self.eventLog.processEvent(WKEvents.WK_EXPORTED)
#
#     def restore(self):
#         self.controller.clearState()
#         self.repository.importWorkspaces()
#
#         workspaces = self.repository.getAllWorkspaces()
#
#         for id, data in workspaces.items():
#             parentID = data.get("parentID")
#
#             self.controller.createWorkspace(id, parentID)
#             self.controller.updateWorkspace(id, data)
#
#         self.eventLog.processEvent(WKEvents.WK_IMPORTED)
