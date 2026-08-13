from clickup import get_clickup_client


async def add_clickup_comment(
    task_id: str,
    comment: str,
    dry_run: bool = True,
) -> dict:
    """
    Add an activity comment to a ClickUp task.

    task_id: ClickUp task ID to comment on.
    comment: Comment text. ClickUp attributes it to the API token owner.
    dry_run: If true, only preview the comment without adding it.
    """

    payload = {
        "task_id": task_id,
        "comment": comment,
    }

    if dry_run:
        return {
            "ok": True,
            "dry_run": True,
            "payload": payload,
        }

    try:
        clickup_client = get_clickup_client()
        result = await clickup_client.add_comment(task_id, comment)
    except ValueError as error:
        return {
            "ok": False,
            "error": str(error),
        }

    return {
        "ok": True,
        "dry_run": False,
        "result": result,
    }


async def create_clickup_task(
    list_id: str,
    name: str,
    description: str | None = None,
    assignees: list[int] | None = None,
    tags: list[str] | None = None,
    priority: int | None = None,
    due_date: int | None = None,
    custom_fields: dict[str, object] | None = None,
    dry_run: bool = True,
) -> dict:
    """
    Create a task in a configured ClickUp list.

    list_id: ClickUp list ID where the task should be created.
    name: Task title.
    description: Optional task description.
    assignees: Optional ClickUp user IDs to assign.
    tags: Optional tag names.
    priority: Optional ClickUp priority value.
    due_date: Optional due date as a Unix timestamp in milliseconds.
    custom_fields: Optional custom field values.
    dry_run: If true, only preview the task payload without creating it.
    """

    payload = {
        "list_id": list_id,
        "name": name,
        "description": description,
        "assignees": assignees or [],
        "tags": tags or [],
        "priority": priority,
        "due_date": due_date,
        "custom_fields": custom_fields or {},
    }

    if dry_run:
        return {
            "ok": True,
            "dry_run": True,
            "payload": payload,
        }

    try:
        clickup_client = get_clickup_client()
        result = await clickup_client.create_task(payload)
    except ValueError as error:
        return {
            "ok": False,
            "error": str(error),
        }

    return {
        "ok": True,
        "dry_run": False,
        "result": result,
    }


async def complete_clickup_task(
    task_id: str,
    comment: str | None = None,
    dry_run: bool = True,
) -> dict:
    """
    Set a ClickUp task to the configured completed status.

    task_id: ClickUp task ID to complete.
    comment: Optional activity comment to add after completing the task.
    dry_run: If true, only preview the update without changing the task.
    """

    clickup_client = get_clickup_client()
    payload = {
        "task_id": task_id,
        "status": clickup_client.completed_status,
        "comment": comment,
    }

    if dry_run:
        return {
            "ok": True,
            "dry_run": True,
            "payload": payload,
        }

    try:
        result = await clickup_client.complete_task(task_id, comment=comment)
    except ValueError as error:
        return {
            "ok": False,
            "error": str(error),
        }

    return {
        "ok": True,
        "dry_run": False,
        "result": result,
    }
