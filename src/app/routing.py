class Packet:
    def __init__(self, data, sender=None, receiver=None, topic=None):
        self.sender = sender
        self.receiver = receiver
        self.topic = topic
        self.data = data


class Endpoint:
    def __init__(self, name: str, dispatcher: "Dispatcher"):
        self.name = name
        self.dispatcher = dispatcher
        self.handlers = {}

    def send(self, body, receiver=None, topic=None):
        packet = Packet(body, sender=self.name, receiver=receiver, topic=None)
        self.dispatcher.send(packet)

    def addHandler(self, key: str, handler):
        self.dispatcher.register(key, handler)


class Dispatcher:
    def __init__(self):
        self.routes = {}

    def register(self, key: str, receiver):
        self.routes.setdefault(key, []).append(receiver)

    def send(self, packet: Packet):
        if packet.receiver:
            receivers = packet.receiver
            if not isinstance(receivers, list):
                receivers = [receivers]
            for r in receivers:
                for cb in self.routes.get(r, []):
                    cb(packet)

        elif packet.topic:
            for cb in self.routes.get(packet.topic, []):
                cb(packet)
