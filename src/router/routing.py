from functools import partial


class RequestType:
    GET = "GET"
    POST = "POST"
    PUT = "PUT"


class Packet:
    def __init__(
        self,
        data,
        method: RequestType,
        resourceID: str = None,
        sender=None,
        receiver=None,
    ):
        self.sender = sender
        self.receiver = receiver
        self.data = data
        self.method = method
        self.resourceID = resourceID


class Endpoint:
    def __init__(self, name: str, dispatcher: "Dispatcher"):
        self.name = name
        self.dispatcher = dispatcher
        self.handlers = {}

    def send(self, body, method, resourceID=None, receiver=None):
        packet = Packet(
            data=body,
            method=method,
            resourceID=resourceID,
            sender=self.name,
            receiver=receiver,
        )
        response = self.dispatcher.send(packet)
        return response

    def addHandler(self, key: str, handler):
        self.dispatcher.register(key, handler)


class Dispatcher:
    def __init__(self):
        self.routes = {}

    def register(self, key: str, receiver):
        self.routes[key] = receiver

    def send(self, packet: Packet):
        if packet.receiver:
            cb = self.routes[packet.receiver]
            response = cb(packet)
            return response


def route(*parts: str) -> str:
    return "/".join(parts)


def routeParts(route: str):
    return route.split("/")


class RouteResolver:
    def __init__(self):
        self.routes = {}

    def addRoute(self, method: RequestType, pathPattern: str, handler):
        key = f"{method} {pathPattern}"
        self.routes[key] = handler

    def resolve(self, method: RequestType, route: str):
        matches = []

        handler = self.routes.get(f"{method} {route}")
        if handler:
            return handler, matches

        for key, handler in self.routes.items():
            routeMethod, routePattern = key.split(" ", 1)
            if routeMethod != method:
                continue

            isMatch, matches = self.matchPattern(route, routePattern)
            if isMatch:
                return handler, matches

    def matchPattern(self, route, pattern):
        routeList = routeParts(route)
        patternList = routeParts(pattern)
        matches = []

        if len(routeList) != len(patternList):
            return False, matches

        for routeP, patternP in zip(routeList, patternList):
            if not patternP.startswith(":"):
                if routeP != patternP:
                    return False, matches

            else:
                matches.append(routeP)

        return True, matches


class EndpointService:
    def __init__(self, name: str, dispatcher: Dispatcher):
        self.endpoint = Endpoint(name, dispatcher)
        self.endpoint.addHandler(name, self.handleRequest)

        self.resolver = RouteResolver()

    def addRoute(self, method: RequestType, resourceID, handler):
        self.resolver.addRoute(method, resourceID, handler)

    def getRouteHandler(self, method: RequestType, resourceID):
        return self.resolver.resolve(method, resourceID)

    def handleRequest(self, packet: Packet):
        handler, params = self.getRouteHandler(packet.method, packet.resourceID)
        handler = partial(handler, *params)
        response = handler(packet.data)
        return response


class Link:
    def __init__(self, baseUrl, *args):
        self.baseUrl = baseUrl
        self.resourceID = route(*args)


class Client:
    def __init__(self, name: str, dispatcher: Dispatcher):
        self.endpoint = Endpoint(name, dispatcher)
        # self.endpoint.addHandler(name, self.handleResponse)

    def _request(self, requestType, link: Link, data=None):
        if data is None:
            data = {}
        return self.endpoint.send(
            data,
            requestType,
            resourceID=link.resourceID,
            receiver=link.baseUrl,
        )

    # def handleResponse(self, packet: Packet):
    #     return packet.data

    def get(self, link: Link, data=None):
        return self._request(RequestType.GET, link, data=data)

    def post(self, link: Link, data=None):
        return self._request(RequestType.POST, link, data=data)

    def put(self, link: Link, data=None):
        return self._request(RequestType.PUT, link, data=data)
