from src.app import App
from src.app.graph.service import GraphService
from src.router.routing import Dispatcher


def main():
    dispatcher = Dispatcher()
    _ = GraphService(dispatcher)
    app = App(dispatcher)
    app.exec()


if __name__ == "__main__":
    main()
