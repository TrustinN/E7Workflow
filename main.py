from app import E7WorkflowApp
from workflows.state import GlobalState

if __name__ == "__main__":
    app = E7WorkflowApp()
    from workflows.runnables.shop import (
        WORKFLOW_NAME,
        initState,
        initWidgets,
        initWorkflow,
        initWorkspaces,
    )
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

    initState(state)
    wkspaces = initWorkspaces()
    wkflow = initWorkflow(wkspaces)
    widgets = initWidgets(wkflow, wkspaces)

    app.addWorkflow(wkflow, wkspaces[WORKFLOW_NAME], state)
    window = app.getWindow(WORKFLOW_NAME)
    for w in widgets:
        window.addWidget(w)

    app.exec()
