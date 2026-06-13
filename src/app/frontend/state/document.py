from dataclasses import asdict

from .layouts import GraphLayout


class Document:
    def __init__(self):
        super().__init__()
        self.fullView = GraphLayout()
        self.miniView = GraphLayout()
        self.workspace = GraphLayout()

        self.layouts = {
            "workspace": self.workspace,
            "fullView": self.fullView,
            "miniView": self.miniView,
        }

    def clear(self):
        for layout in self.layouts.values():
            layout.clear()

    def serialize(self):
        return {name: asdict(layout) for name, layout in self.layouts.items()}

    def deserialize(self, data):
        for name, layout in data.items():
            self.layouts[name].deserialize(layout)
