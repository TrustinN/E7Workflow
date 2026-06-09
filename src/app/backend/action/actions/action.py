import time

DEFAULT_SLEEP_TIME = 0.3


class Action:
    def __init__(self, name, sleep=DEFAULT_SLEEP_TIME):
        self.name = name
        self.sleep = sleep

    def info():
        pass

    def action(self, data):
        pass

    def execute(self, data):
        self.action(data)
        time.sleep(self.sleep)
