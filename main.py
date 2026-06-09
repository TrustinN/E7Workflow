from src.app import App
from src.app.backend.action import ActionService
from src.router.routing import Dispatcher


def main():
    dispatcher = Dispatcher()

    _ = ActionService(dispatcher)

    app = App(dispatcher)
    app.exec()


if __name__ == "__main__":
    main()
