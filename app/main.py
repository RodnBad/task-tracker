"""Task Tracker — FastAPI application."""

from datetime import date
from typing import Optional

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from app import storage
from app.business_rules import assert_valid_transition
from app.models import Task, TaskCreate, TaskUpdate

app = FastAPI(
    title="Task Tracker",
    description="AI-Assisted Coding mid-course project — Task Tracker with due dates and tags.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", tags=["health"])
def health_check() -> dict:
    """Confirm the API is running."""
    return {"status": "ok"}


@app.post("/tasks", response_model=Task, status_code=201, tags=["tasks"])
def create_task(payload: TaskCreate) -> Task:
    """Create a new task."""
    task = Task(
        title=payload.title,
        description=payload.description,
        due_date=payload.due_date,
        tags=payload.tags,
    )
    return storage.save(task)


@app.get("/tasks", response_model=list[Task], tags=["tasks"])
def list_tasks(
    overdue: Optional[bool] = Query(default=None),
    tag: Optional[str] = Query(default=None),
) -> list[Task]:
    """List all tasks. Filters: overdue=true, tag=<label>. Combinable."""
    tasks = storage.get_all()
    if overdue is True:
        today = date.today()
        tasks = [t for t in tasks if t.due_date and t.due_date < today and t.status != "done"]
    if tag is not None:
        tasks = [t for t in tasks if tag in t.tags]
    return tasks


@app.get("/tasks/{task_id}", response_model=Task, tags=["tasks"])
def get_task(task_id: str) -> Task:
    """Retrieve a single task by ID."""
    task = storage.get_by_id(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail=f"Task '{task_id}' not found.")
    return task


@app.put("/tasks/{task_id}", response_model=Task, tags=["tasks"])
def update_task(task_id: str, payload: TaskUpdate) -> Task:
    """Update a task. Status transitions: todo->in_progress->done, in_progress->todo."""
    task = storage.get_by_id(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail=f"Task '{task_id}' not found.")
    if payload.status is not None and payload.status != task.status:
        try:
            assert_valid_transition(task.status, payload.status)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc))
    update_dict = {k: getattr(payload, k) for k in payload.model_fields_set}
    updated = task.model_copy(update=update_dict)
    return storage.save(updated)


@app.delete("/tasks/{task_id}", status_code=204, tags=["tasks"])
def delete_task(task_id: str) -> None:
    """Delete a task by ID."""
    if not storage.delete(task_id):
        raise HTTPException(status_code=404, detail=f"Task '{task_id}' not found.")
