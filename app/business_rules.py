"""Business rules for Task Tracker — status transition validation."""

from app.models import TaskStatus

# Only these (from, to) pairs are permitted. Same-status "no-op" updates
# are rejected too — the check is on the (current, new) pair, not on
# enum validity of `new` alone.
VALID_TRANSITIONS: frozenset[tuple[TaskStatus, TaskStatus]] = frozenset({
    (TaskStatus.TODO,        TaskStatus.IN_PROGRESS),
    (TaskStatus.IN_PROGRESS, TaskStatus.DONE),
    (TaskStatus.DONE,        TaskStatus.IN_PROGRESS),   # a completed task can be reopened
})


def is_valid_transition(current: TaskStatus, new: TaskStatus) -> bool:
    """Return True if transitioning from current → new is allowed."""
    return (current, new) in VALID_TRANSITIONS


def assert_valid_transition(current: TaskStatus, new: TaskStatus) -> None:
    """Raise ValueError if the transition is not allowed."""
    if not is_valid_transition(current, new):
        raise ValueError(
            f"Invalid status transition: '{current.value}' → '{new.value}'. "
            f"Allowed transitions: ToDo→InProgress, InProgress→Done, Done→InProgress."
        )
