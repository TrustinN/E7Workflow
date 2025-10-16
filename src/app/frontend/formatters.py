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
