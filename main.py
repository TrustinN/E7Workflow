from app import E7WorkflowApp, GlobalState

if __name__ == "__main__":
    app = E7WorkflowApp()
    from workflows.penguin import bindToApp as bindPenguinToApp
    from workflows.shop import bindToApp as bindShopToApp

    state = GlobalState()
    bindShopToApp(app, state)
    bindPenguinToApp(app, state)
    app.exec()
