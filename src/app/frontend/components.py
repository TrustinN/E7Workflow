from .formatters import OutputFormatter


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
