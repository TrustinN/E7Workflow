from app import E7WorkflowApp

if __name__ == "__main__":
    app = E7WorkflowApp()
    from workflows.nav import homeWorkflow
    from workflows.penguin import penguinWorkflow
    from workflows.shop import shopWorkflow

    app.addWorkflow(shopWorkflow)
    app.addWorkflow(penguinWorkflow)
    app.addWorkflow(homeWorkflow)
    app.exec()
