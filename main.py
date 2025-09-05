from src.app import App
from src.app.graph import GraphService
from src.app.workspace import WorkspaceService
from src.router.routing import Dispatcher


def main():
    dispatcher = Dispatcher()
    _ = GraphService(dispatcher)
    _ = WorkspaceService(dispatcher)
    app = App(dispatcher)
    app.exec()


if __name__ == "__main__":
    main()
