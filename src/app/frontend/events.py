from functools import partial

from nanoid import generate

from .formatters import OutputFormatter


class EventIDProvider:
    def __init__(self, group: str):
        self.group = group
        self.groupID = group + generate(size=8)
        self.counter = 0

    def genID(self):
        id = f"{self.groupID}__{self.counter}"
        self.counter += 1
        return id


class AppEvents:
    provider = EventIDProvider("ApplicationEvent")

    APP_LOADED = provider.genID()

    NODE_PRESSED = provider.genID()


class EventLog:
    def __init__(self):
        self.handlers: dict[str, list[any]] = {}

    def register(self, event: str, handler):
        self.handlers.setdefault(event, []).append(handler)

    def processEvent(self, event: str, data=None):
        if event not in self.handlers:
            return
        handlers = self.handlers[event]
        for cb in handlers:
            cb(data or {})


class PyQtSignalAdaptor:
    def __init__(self, signal, formatter: OutputFormatter = None):
        self.signal = signal
        self.formatter = formatter

    def connect(self, callback):

        def wrapped(*args):
            if self.formatter:
                data = self.formatter.format(args)
            else:
                # Fallback: convert args tuple into numbered dict
                data = {}
            callback(data)

        self.signal.connect(wrapped)


class EventHandler:
    def __init__(self, handler, data=True):
        self.handler = handler
        self.data = data

        self.lastHandler: EventHandler = self
        self.nextHandler = None

    def _setNext(self, handler: "EventHandler"):
        self.nextHandler = handler

    def chain(self, handler, data=True):
        nextHandler = EventHandler(handler, data)
        self.lastHandler._setNext(nextHandler)
        self.lastHandler = nextHandler.lastHandler
        return self

    def __call__(self, data):
        output = None
        if self.data:
            output = self.handler(data)
        else:
            output = self.handler()

        newData = data.copy()
        if output:
            newData.update(output)
        if self.nextHandler is not None:
            self.nextHandler(newData)


def inject(getData):
    def updateData(data):
        data = data.copy()
        data.update(getData())
        return data

    return updateData


def emitHandler(eventLog: EventLog, signal):
    return partial(eventLog.processEvent, signal)


def subscribe(eventlog: EventLog, event: str, handler):
    eventlog.register(event, handler)
