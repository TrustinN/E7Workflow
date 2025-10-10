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
        self.data = data

    def save(self):
        data = self.toDict()
        with open("context", "w") as f:
            json.dump(data, f, indent=4)

    def load(self):
        with open("context", "r") as f:
            data = json.load(f)
            self.fromDict(data)
