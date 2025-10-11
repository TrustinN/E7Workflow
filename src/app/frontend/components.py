class OutputFormatter:
    def __init__(self):
        pass

    def format(self, output):
        pass


class JsonFormatter(OutputFormatter):
    def __init__(self, labels):
        super().__init__()
        self.labels = labels

    def format(self, output):
        if output is None:
            return {}

        elif isinstance(output, tuple):
            kvPairs = zip(self.labels, output)
            return dict([(label, out) for label, out in kvPairs])

        else:
            return {self.labels[0]: output}


class Capability:
    def __init__(self, name, func, reformat: OutputFormatter = None):
        self.name = name
        self.func = func
        self.reformat = reformat

    def __call__(self, *args, **kwargs):
        res = self.func(*args, **kwargs)
        if self.reformat is None:
            return res

        return self.reformat.format(res)


class Component:
    def __init__(self):
        self.capabilities = {}

    def useAction(self, capability: str):
        return self.capabilities[capability]

    def registerCapability(self, capability: Capability):
        self.capabilities[capability.name] = capability


class Serializer:
    def __init__(self):
        pass

    def restore(self):
        pass

    def export(self):
        pass


class EventDispatcher:
    def __init__(self):
        self.receivers = []

    def register(self, receiver):
        self.receivers.append(receiver)

    def process(self, topic, data):
        for receiver in self.receivers:
            receiver.process(topic, data)


class EventReceiver:
    def __init__(self, dispatcher: EventDispatcher):
        self.callbacks = {}

    def register(self, topic, cb):
        self.callbacks.setdefault(topic, []).append(cb)

    def process(self, topic, data):
        for cb in self.callbacks[topic]:
            cb(data)
