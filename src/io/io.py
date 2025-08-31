import json


class LogEntry:
    def __init__(self, replay, params: dict[str, any]):
        self.replay = replay
        self.params = params


class Serializer:
    def __init__(self, obj, funcMap):
        self.obj = obj
        self.funcMap = funcMap
        self.logs = []

    def addLog(self, funcName, params: dict[str, any]):
        replay = self.funcMap[funcName]
        self.logs.append(LogEntry(replay, params))

    def playLog(self, log):
        log.replay(self.obj, **log.params)

    def playLogs(self):
        for log in self.logs:
            self.playLog(log)

    def serializeLog(self, log: LogEntry):
        return {
            "replay": log.replay.__name__,
            "params": log.params,
        }

    def deserializeLog(self, data):
        replay = self.funcMap[data["replay"]]
        params = data["params"]
        return LogEntry(replay, params)

    def serializeLogs(self):
        return json.dumps([self.serializeLog(log) for log in self.logs], indent=2)

    def deserializeLogs(self, data):
        logData = json.loads(data)
        self.logs = [self.deserializeLog(arg) for arg in logData]

    def writeData(self, filename):
        with open(filename, "w") as file:
            file.write(self.serializeLogs())

    def readData(self, filename):
        with open(filename, "r") as file:
            self.deserializeLogs(file.read())

    def reset(self):
        self.logs = []
