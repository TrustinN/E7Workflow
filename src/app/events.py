from PyQt5.QtCore import QObject, pyqtSignal


class Node(QObject):
    publish_ = pyqtSignal(str, dict)

    def __init__(self):
        super().__init__()
        self.subscriptionList_ = {}

    def publish(self, route: str, msg=None):
        if msg is None:
            msg = {}
        self.publish_.emit(route, msg)

    def subscribe(self, route: str, cb):
        self.subscriptionList_[route] = cb


class EventBus:
    def __init__(self):
        self.nodes: list[Node] = []

    def registerNode(self, node: Node):
        node.publish_.connect(self.handlePublish)
        self.nodes.append(node)

    def registerNodes(self, nodes: list[Node]):
        for node in nodes:
            self.registerNode(node)

    def handlePublish(self, route: str, msg=None):
        for node in self.nodes:
            cb = node.subscriptionList_.get(route)
            if not cb:
                continue

            cb(msg)
