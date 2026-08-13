# Internal MCP Server

This MCP server provides internal developer workflow tools for notifications,
database operations, and ClickUp task management.

## ClickUp configuration

Set the following environment variable before starting the server:

```env
CLICKUP_API_TOKEN=pk_your_clickup_token
```

Optional settings:

```env
CLICKUP_API_URL=https://api.clickup.com/api/v2
CLICKUP_COMPLETED_STATUS=complete
```

`CLICKUP_COMPLETED_STATUS` must match a closed status available in the target
ClickUp list.

## ClickUp actions

All ClickUp actions default to `dry_run=true`. Set `dry_run=false` only when the
operation should be sent to ClickUp.

### Natural-language examples

When using this server through an MCP client, you can ask for ClickUp operations
in ordinary language. For example:

> Create a task for testing under project Grammata.

The agent should use the provider's list-discovery methods to find the ClickUp
folder or list named `Grammata`, select its target list, and call
`create_clickup_task`. If more than one matching list exists, it should ask
which one to use before creating anything.

The Grammata test-task request above is equivalent to an MCP call like:

```json
{
  "list_id": "901524037834",
  "name": "MCP server test task",
  "description": "Created by the internal MCP server to verify the ClickUp integration.",
  "dry_run": false
}
```

Other example requests:

> Dry-run completing task WIA-4075.

> Complete task WIA-4075 and add the comment "Closed using the MCP server."

> Add the comment "real author: Armando Schiano di Cola" to WIA-4075.

For custom task IDs such as `WIA-4075`, the agent must resolve the custom ID to
ClickUp's internal task ID before calling the current completion or comment
action. Dry-run requests must only return a preview and must not contact ClickUp
or modify the task.

### Create a task

Use `create_clickup_task` with a ClickUp list ID and task name:

```json
{
  "list_id": "901512983244",
  "name": "Investigate failed import",
  "description": "Review the latest import logs.",
  "assignees": [94598521],
  "tags": ["support"],
  "priority": 2,
  "due_date": 1786586400000,
  "custom_fields": {},
  "dry_run": true
}
```

`due_date` is a Unix timestamp in milliseconds. Custom fields are supplied as a
mapping from ClickUp field ID to value.

### Complete a task

Use `complete_clickup_task` with ClickUp's internal task ID:

```json
{
  "task_id": "86cb4t7jt",
  "comment": "Closed using the MCP server.",
  "dry_run": false
}
```

The optional `comment` is added after the task is completed. If adding the
comment fails, the task may already be complete.

Custom task IDs such as `WIA-4075` require a ClickUp workspace/team ID when used
with the ClickUp API. The current MCP actions expect the internal task ID, which
is returned by ClickUp as the task's `id` field.

### Add a comment

Use `add_clickup_comment` to add an activity comment without changing task
status:

```json
{
  "task_id": "86cb4t7jt",
  "comment": "real author: Armando Schiano di Cola",
  "dry_run": false
}
```

ClickUp always attributes API comments to the user who owns
`CLICKUP_API_TOKEN`. The API does not allow callers to override or impersonate
the comment author. When another person is the real author, include that
attribution in the comment text.

## Provider discovery examples

ClickUp hierarchy discovery is implemented on `ClickUpNotificationProvider` so
agents and application code do not need ad hoc scripts:

```python
from notification_providers.clickup import ClickUpNotificationProvider

provider = ClickUpNotificationProvider()

workspaces = await provider.get_workspaces()
spaces = await provider.get_spaces(workspace_id="9006042609")
folders = await provider.get_folders(space_id="90040148906")
folderless_lists = await provider.get_folderless_lists(space_id="90040148906")
grammata_lists = await provider.find_lists("Grammata")
```

`find_lists()` returns matching list IDs together with their folder, space, and
workspace location. These discovery methods are provider methods rather than
ad hoc scripts.

## ClickUp discovery tools

Use `find_clickup_lists` before creating a task when only a list or project name
is known. It searches list and folder names and returns the numeric list ID with
its workspace, space, and folder location.

Use `find_clickup_users` before assigning a task when only a person's name or
email address is known. It returns matching numeric user IDs and their workspace
locations. Both tools perform case-insensitive partial matching and are
read-only.

Agents should use these discovery tools instead of passing names as IDs or
silently omitting requested assignees. If discovery returns multiple matches,
ask the user to select the intended result before creating the task.

## Running the server

Run the stdio MCP server with:

```shell
uv run python server.py
```
