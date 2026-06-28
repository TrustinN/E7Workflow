from src.app.events import Node
from src.router.routing import Dispatcher

from .model import RuntimeModel
from .service import RuntimeService
from .ui import RuntimeEditor


class RuntimeComponent(Node):
    def __init__(self, dispatcher: Dispatcher):
        super().__init__()

        self.model = RuntimeModel()
        self.service = RuntimeService(self.model, dispatcher)

        self.editor = RuntimeEditor(self.model)
