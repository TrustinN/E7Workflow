import time

DEFAULT_SLEEP_TIME = 0.3


class Action:
    def __init__(self, sleep=DEFAULT_SLEEP_TIME):
        self.sleep = sleep

    @classmethod
    def info(cls):
        pass

    @classmethod
    def icon(cls, data):
        pass

    def action(self, data):
        pass

    def execute(self, data):
        result = self.action(data)
        time.sleep(self.sleep)
        return result
