import src.app.resources
from src.app import App
from src.router.routing import Dispatcher


def main():
    dispatcher = Dispatcher()

    app = App(dispatcher)
    app.exec()


if __name__ == "__main__":
    main()
