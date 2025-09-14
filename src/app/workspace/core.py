from src.router.routing import Client, Dispatcher

from .widget import WorkspaceWidget


class WorkspaceCore:
    def __init__(self, widget: WorkspaceWidget, dispatcher: Dispatcher):
        self.widget = widget
        self.client = Client("Workspace Core", dispatcher)
