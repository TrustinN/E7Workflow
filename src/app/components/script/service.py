import math

import cv2
import numpy as np

from src.router.routing import Dispatcher, EndpointService, RequestType, route

from .model import ScriptModel


class ScriptRoute:
    NAME = "ScriptService"
    SCRIPT = "SCRIPT"


class ScriptService(EndpointService):

    def __init__(self, model: ScriptModel, dispatcher: Dispatcher):
        super().__init__(ScriptRoute.NAME, dispatcher)

        self.model = model

        # Get data about action like user params
        getRoute = route(ScriptRoute.SCRIPT)
        self.addRoute(RequestType.GET, getRoute, self.getScript)

        runRoute = route(ScriptRoute.SCRIPT, ":id")
        self.addRoute(RequestType.POST, runRoute, self.runScript)

    def getScript(self, data):
        return {"id": self.model.getActiveScript()}

    def runScript(self, id, data):
        schema = self.model.getScript(id)
        namespace = {
            "__builtins__": __builtins__,
            "math": math,
            "np": np,
            "cv2": cv2,
        }

        exec(schema.code, namespace)
        result = namespace["condition"](data)
        return {"result": result}
