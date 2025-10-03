from src.router.routing import Client, Dispatcher, Link

from ..event.events import Event, EventLog, EventType


class Core:
    def __init__(self, dispatcher: Dispatcher):
        self.client = Client("App Core", dispatcher)

    def createWorkspace(self):
        self.
