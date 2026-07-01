from pynput import keyboard

import src.app.resources
from src.app import App
from src.router.routing import Dispatcher


def on_press(key):
    pass


def main():
    dispatcher = Dispatcher()

    app = App(dispatcher)

    def on_release(key):
        if key == keyboard.Key.esc:
            app.quit()
            return False

    listener = keyboard.Listener(on_press=on_press, on_release=on_release)
    listener.start()

    app.exec()


if __name__ == "__main__":
    main()
