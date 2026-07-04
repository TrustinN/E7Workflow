# E7Workflow

E7Workflow is an automation tool that allows users to create workflows by assigning actions to screen regions and connecting them with an execution graph.

## Demo
<video src=https://github.com/TrustinN/E7Workflow/releases/download/v0.1.0-demo/demo.mp4
       controls
       autoplay
       loop
       muted
       width="800">
</video>

## Usage

Clone the repo:

```
git clone https://github.com/TrustinN/E7Workflow.git
cd E7Workflow
```

Create a virtual environment and install the requirements:

```
python -m pip install -r requirements.txt
```

## Description

### Workspaces

The workspaces are resizable components in which an action can execute on. The root workspace must always exist and direct children of the root are assigned a grouping from A-Z. These groupings are for the user's convenience when creating a workspace for a particular workflow. Workspace visibility can be toggled in the Workspace View panel. Locking the workspace in the view panel prevents the workspace from receiving mouse events and is useful for preserving the layout when a parent is selected and moved.

### Graph

Edges define the order in which a graph execution moves. Edges can be assigned a script written in the Scripts panel to determine whether or not the edge is traversed. The condition(context) function receives a dictionary in which the current execution context can be used (more on context later). The priority can be assigned in the runner panel to dictate which edges are considered for traversal first.

### Actions

Actions are stateless functions that can be assigned to a graph node/workspace for execution. They can be assigned to the currently selected workspace in the Actions panel. Pre-actions and post-actions can be defined under the Runner panel, and are built to modify the context. Both these functions receive the context object while post-actions also receive the action result, which is defined in the schema under the Actions panel for each action.

### Context

The context can be modified during execution for usage in post-actions. Currently, the supported datatypes to be saved are numbers, strings, and images. Double clicking on an image context allows the user to select a file to their own image to be imported.

### Shortcuts

See `src/app/app.py` for the shortcut keys. Some shortcuts are labeled on the buttons in the UI, however deleting an edge (delete button) is not.

## Emergency Stop

Pressing `Esc` force-closes the application and can be used to stop workflow execution. This only works if the target application does not consume the key press before E7Workflow receives it. Please test this before running a workflow
