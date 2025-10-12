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
            data = {}
            for i in range(len(self.labels)):
                label = self.labels[i]
                data[label] = output[i]

            return data

        else:
            return {self.labels[0]: output}


class Capability:
    def __init__(self, func, reformat: OutputFormatter = None):
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

    def registerCapability(self, name: str, capability: Capability):
        self.capabilities[name] = capability


class Serializer:
    def __init__(self):
        pass

    def restore(self):
        pass

    def export(self):
        pass
