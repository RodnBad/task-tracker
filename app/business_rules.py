"""Business rules for Task Tracker — status transition validation."""

from app.models import TaskStatus

# Only these (from, to) pairs are permitted
VALID_TRANSITIONS: frozenset[tuple[TaskStatus, TaskStatus]] = frozenset({
    (TaskStatus.todo,        TaskStatus.in_progress),
    (TaskStatus.in_progress, TaskStatus.done),
    (TaskStatus.in_progress, TaskStatus.todo),   # revert
})


def is_valid_transition(current: TaskStatus, new: TaskStatus) -> bool:
    """Return True if transitioning from current → new is allowed."""
    if current == new:
        return True  # no-op is always fine
    return (current, new) in VALID_TRANSITIONS


def assert_valid_transition(current: TaskStatus, new: TaskStatus) -> None:
    """Raise ValueError if the transition is not allowed."""
    if not is_valid_transition(current, new):
        raise ValueError(
            f"Invalid status transition: '{current}' → '{new}'. "
            f"Allowed transitions: todo→in_progress, in_progress→done, in_progress→todo."
        )
