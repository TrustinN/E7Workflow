class EventType:
    APPLICATION_LOADED = 1

    WORKSPACE_CREATED = 2
    WORKSPACE_UPDATED = 3
    WORKSPACE_FOCUSED = 4

    NODE_PRESSED = 5


class EventLog:
    def __init__(self):
        self.handlers: dict[EventType, list[any]] = {}

    def register(self, event: EventType, handler):
        self.handlers.setdefault(event, []).append(handler)

    def processEvent(self, eventType, data=None):
        if eventType not in self.handlers:
            return
        handlers = self.handlers[eventType]
        for cb in handlers:
            cb(data or {})


def subscribe(eventlog: EventLog, event: str, handler):
    eventlog.register(event, handler)
