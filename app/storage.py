"""In-memory task storage."""

from app.models import Task

# Single source of truth for all tasks in this process
_store: dict[str, Task] = {}


def get_all() -> list[Task]:
    """Return all tasks."""
    return list(_store.values())


def get_by_id(task_id: str) -> Task | None:
    """Return a task by ID, or None if not found."""
    return _store.get(task_id)


def save(task: Task) -> Task:
    """Insert or replace a task."""
    _store[task.id] = task
    return task


def delete(task_id: str) -> bool:
    """Delete a task. Returns True if it existed."""
    if task_id in _store:
        del _store[task_id]
        return True
    return False


def clear() -> None:
    """Remove all tasks. Used in tests to reset state."""
    _store.clear()
