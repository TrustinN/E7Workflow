from app import E7WorkflowApp
from workflows.state import GlobalState

if __name__ == "__main__":
    app = E7WorkflowApp()
    import workflows.runnables.custom as custom
    import workflows.runnables.penguin.buy as pgnb
    import workflows.runnables.shop as shop
    from workflows.state import (
        bookmarkManager,
        currencyManager,
        penguinManager,
        windowManager,
    )

    managers = [currencyManager, bookmarkManager, penguinManager, windowManager]

    state = GlobalState()
    for m in managers:
        m.attachState(state)
        m.initState()

    modules = [shop, pgnb, custom]
    for module in modules:
        module.initState(state)
        wkspaces = module.initWorkspaces()
        wkflow = module.initWorkflow(wkspaces)
        widgets = module.initWidgets(wkflow, wkspaces)

        app.addWorkflow(wkflow, wkspaces[module.WORKFLOW_NAME], state)
        window = app.getWindow(module.WORKFLOW_NAME)
        for w in widgets:
            window.addWidget(w)

    app.exec()
