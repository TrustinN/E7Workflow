class RequestType:
    GET = "GET"
    POST = "POST"
    PUT = "PUT"


class Packet:
    def __init__(
        self,
        data,
        method: RequestType,
        resourceID: str = None,
        sender=None,
        receiver=None,
        topic=None,
    ):
        self.sender = sender
        self.receiver = receiver
        self.topic = topic
        self.data = data
        self.method = method
        self.resourceID = resourceID


class Endpoint:
    def __init__(self, name: str, dispatcher: "Dispatcher"):
        self.name = name
        self.dispatcher = dispatcher
        self.handlers = {}

    def send(self, body, method, resourceID=None, receiver=None, topic=None):
        packet = Packet(
            data=body,
            method=method,
            resourceID=resourceID,
            sender=self.name,
            receiver=receiver,
            topic=topic,
        )
        response = self.dispatcher.send(packet)
        return response

    def addHandler(self, key: str, handler):
        self.dispatcher.register(key, handler)


class Dispatcher:
    def __init__(self):
        self.routes = {}

    def register(self, key: str, receiver):
        self.routes[key] = receiver

    def send(self, packet: Packet):
        if packet.receiver:
            cb = self.routes[packet.receiver]
            response = cb(packet)
            return response


def route(*parts: str) -> str:
    return "/".join(parts)


class EndpointService:
    def __init__(self, name: str, dispatcher: Dispatcher):
        self.endpoint = Endpoint(name, dispatcher)
        self.endpoint.addHandler(name, self.handleRequest)
        self.routes = {}

    def addRoute(self, method: RequestType, resourceID, handler):
        self.routes[f"{method} {resourceID}"] = handler

    def getRouteHandler(self, method: RequestType, resourceID):
        return self.routes[f"{method} {resourceID}"]

    def subscribe(self, name: str, handler):
        self.endpoint.addHandler(name, handler)

    def handleRequest(self, packet: Packet):
        handler = self.getRouteHandler(packet.method, packet.resourceID)
        response = handler(packet.data)
        return response
