from app import E7WorkflowApp
from workflows.nav import buildHomeWorkflow
from workflows.penguin import buildWorkflow as buildPenguinWorkflow
from workflows.shop import buildWorkflow as buildShopWorkflow

if __name__ == "__main__":
    app = E7WorkflowApp()

    penguinWorkflow = buildPenguinWorkflow()
    shopWorkflow = buildShopWorkflow()
    homeWorkflow = buildHomeWorkflow()
    app.addWorkflow(shopWorkflow)
    app.addWorkflow(penguinWorkflow)
    app.addWorkflow(homeWorkflow)
    app.exec()
