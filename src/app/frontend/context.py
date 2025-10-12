import json


class Context:
    def __init__(self):
        self.data = {}

    def get(self, field):
        return self.data[field]

    def add(self, field, value=None):
        self.data[field] = value

    def put(self, field, value):
        self.data[field] = value

    def toDict(self):
        return self.data.copy()

    def fromDict(self, data):
        self.data.clear()
        self.data.update(data)


class ContextManager:
    def __init__(self):
        self.contexts = {}

    def addContext(self, ctxID: str):
        context = Context()
        self.contexts[ctxID] = context

        return context

    def getContext(self, ctxID: str):
        return self.contexts[ctxID]

    def saveContext(self):
        ctxAccum = {}
        for ctxID in self.contexts:
            ctx = self.contexts[ctxID]
            ctxAccum[ctxID] = ctx.toDict()

        with open("context", "w") as f:
            json.dump(ctxAccum, f, indent=4)

    def loadContext(self):
        with open("context", "r") as f:
            ctxAccum = json.load(f)
            for ctxID in ctxAccum:
                data = ctxAccum[ctxID]

                context = self.contexts[ctxID]
                context.fromDict(data)
