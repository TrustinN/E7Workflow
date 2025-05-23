from app import E7WorkflowApp
from workflows.state import GlobalState

if __name__ == "__main__":
    app = E7WorkflowApp()
    from workflows.runnable.custom import bindToApp as bindShopAndPenguinToApp
    from workflows.state import (
        bookmarkManager,
        currencyManager,
        penguinManager,
        windowManager,
    )

    managers = [currencyManager, bookmarkManager, penguinManager, windowManager]

    state = GlobalState()
    for m in managers:
        m.initState(state)

    # bindShopToApp(app, state)
    # bindPenguinToApp(app, state)
    bindShopAndPenguinToApp(app, state)
    app.exec()
