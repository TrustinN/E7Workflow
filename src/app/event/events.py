class EventType:
    APPLICATION_LOADED = 1
    WORKSPACE_CREATED = 2
    WORKSPACE_UPDATED = 3
    WORKSPACE_FOCUSED = 4


class Event:
    def __init__(self, eventType: EventType, data=None):
        self.eventType = eventType
        self.data = data


class EventLog:
    def __init__(self):
        self.handlers: dict[EventType, list[any]] = {}

    def register(self, event: EventType, handler):
        self.handlers.setdefault(event, []).append(handler)

    def processEvent(self, event: Event):
        if event.eventType not in self.handlers:
            return
        handlers = self.handlers[event.eventType]
        for cb in handlers:
            cb(event.data or {})


def subscribe(eventlog: EventLog, event: str, handler):
    eventlog.register(event, handler)
