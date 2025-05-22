from app import E7WorkflowApp, GlobalState

if __name__ == "__main__":
    app = E7WorkflowApp()
    from workflows.custom import bindToApp as bindShopAndPenguinToApp
    from workflows.penguin.buy import bindToApp as bindPenguinToApp
    from workflows.shop import bindToApp as bindShopToApp
    from workflows.state.inventory.bookmark import bookmarkManager
    from workflows.state.inventory.currency import currencyManager
    from workflows.state.inventory.penguin import penguinManager
    from workflows.state.window import windowManager

    managers = [currencyManager, bookmarkManager, penguinManager, windowManager]

    state = GlobalState()
    for m in managers:
        m.initState(state)

    bindShopToApp(app, state)
    bindPenguinToApp(app, state)
    bindShopAndPenguinToApp(app, state)
    app.exec()
