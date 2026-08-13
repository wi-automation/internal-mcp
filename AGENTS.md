# Repository instructions

## Scope

This repository implements an internal MCP server. Keep tool functions in
`tools/`, external service implementations in their provider or client module,
and register new MCP tools in `server.py` and `tools/__init__.py`.

## ClickUp operations

- Use `create_clickup_task` to create tasks, `complete_clickup_task` to close
  tasks, and `add_clickup_comment` to add activity comments.
- Keep `dry_run=true` unless the user explicitly authorizes the external
  mutation. A dry run must not call ClickUp.
- Use ClickUp's internal task ID for completion and comment actions. Values such
  as `WIA-4075` are custom IDs and must first be resolved to an internal ID.
- Never display or log `CLICKUP_API_TOKEN`.
- ClickUp attributes comments to the account that owns the configured API
  token. Do not claim that a comment was posted as another user. If requested,
  put the real-author attribution in the comment text.
- `complete_clickup_task` updates the task before adding its optional comment.
  Report partial success accurately if the comment request fails.
- Add reusable ClickUp discovery operations, such as workspace, project/folder,
  and list lookup, to `ClickUpNotificationProvider`. Do not create temporary
  scripts or files for ClickUp API discovery.

## Implementation and verification

- Preserve the provider's `ValueError` error contract so MCP tools can return a
  structured `{ "ok": false, "error": ... }` response.
- New mutating tools must default to dry-run mode and return a preview payload.
- Run `uv run ruff check .` and targeted Python compilation after changes.
- Do not make real external API calls during verification unless the user
  explicitly requested the corresponding mutation.
