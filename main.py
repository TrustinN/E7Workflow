from src.app import App
from src.app.graph import GraphBackend, GraphService
from src.app.workspace import WorkspaceBackend, WorkspaceService
from src.router.routing import Dispatcher


def main():
    dispatcher = Dispatcher()
    graphBackend = GraphBackend()
    workspaceBackend = WorkspaceBackend()
    _ = GraphService(dispatcher, graphBackend)
    _ = WorkspaceService(dispatcher, workspaceBackend)
    app = App(dispatcher)
    app.exec()


if __name__ == "__main__":
    main()
