import math

import cv2
import numpy as np

from src.router.routing import Dispatcher, EndpointService, RequestType, route

from .model import ScriptModel, ScriptViewModel


class ScriptRoute:
    NAME = "ScriptService"
    SCRIPT = "SCRIPT"


class ScriptService(EndpointService):

    def __init__(
        self,
        model: ScriptModel,
        viewModel: ScriptViewModel,
        dispatcher: Dispatcher,
    ):
        super().__init__(ScriptRoute.NAME, dispatcher)

        self.model = model
        self.viewModel = viewModel

        scriptRoute = route(ScriptRoute.SCRIPT)
        self.addRoute(RequestType.GET, scriptRoute, self.getScript)

        idRoute = route(ScriptRoute.SCRIPT, ":id")
        self.addRoute(RequestType.GET, idRoute, self.getScriptByID)
        self.addRoute(RequestType.POST, idRoute, self.runScript)

    def getScript(self, data):
        return {"id": self.viewModel.getActiveScript()}

    def getScriptByID(self, id, data):
        return self.model.getScript(id).toData()

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
