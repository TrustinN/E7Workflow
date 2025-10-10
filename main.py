from src.app import App
from src.app.backend.graph import GraphBackend, GraphService
from src.app.backend.runner import RunnerBackend, RunnerService
from src.app.backend.workspace import WorkspaceBackend, WorkspaceService
from src.router.routing import Dispatcher


def main():
    dispatcher = Dispatcher()

    workspaceBackend = WorkspaceBackend()
    graphBackend = GraphBackend()
    runnerBackend = RunnerBackend()

    _ = WorkspaceService(dispatcher, workspaceBackend)
    _ = GraphService(dispatcher, graphBackend)
    _ = RunnerService(dispatcher, runnerBackend)

    app = App(dispatcher)
    app.exec()


if __name__ == "__main__":
    main()
