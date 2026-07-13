"""Pydantic v2 data models for Task Tracker."""

from __future__ import annotations

from datetime import date
from enum import Enum
from typing import Optional
from uuid import uuid4

from pydantic import BaseModel, Field, field_validator

# Tag limits (see docs/midcourse/mini-adr.md, ADR-05)
MAX_TAGS = 10
MAX_TAG_LENGTH = 30


class TaskStatus(str, Enum):
    """Valid task statuses."""
    todo = "todo"
    in_progress = "in_progress"
    done = "done"


def _clean_tags(tags: list[str]) -> list[str]:
    """Trim whitespace and reject empty or over-limit tags."""
    cleaned = []
    for tag in tags:
        trimmed = tag.strip()
        if not trimmed:
            raise ValueError("Tags must not be empty or whitespace-only.")
        if len(trimmed) > MAX_TAG_LENGTH:
            raise ValueError(f"Tag '{trimmed}' exceeds max length of {MAX_TAG_LENGTH} characters.")
        cleaned.append(trimmed)
    if len(cleaned) > MAX_TAGS:
        raise ValueError(f"A task may have at most {MAX_TAGS} tags.")
    return cleaned


class TaskCreate(BaseModel):
    """Payload for creating a new task."""
    title: str = Field(..., min_length=1, max_length=200)
    description: str = Field(default="")
    due_date: Optional[date] = Field(default=None, description="Optional due date (YYYY-MM-DD)")
    tags: list[str] = Field(default_factory=list, description="List of label tags")

    @field_validator("tags")
    @classmethod
    def validate_tags(cls, value: list[str]) -> list[str]:
        return _clean_tags(value)


class TaskUpdate(BaseModel):
    """Payload for updating an existing task (all fields optional)."""
    title: Optional[str] = Field(default=None, min_length=1, max_length=200)
    description: Optional[str] = None
    status: Optional[TaskStatus] = None
    due_date: Optional[date] = None
    tags: Optional[list[str]] = None

    @field_validator("tags")
    @classmethod
    def validate_tags(cls, value: Optional[list[str]]) -> Optional[list[str]]:
        if value is None:
            return value
        return _clean_tags(value)


class Task(BaseModel):
    """Full task representation stored and returned by the API."""
    id: str = Field(default_factory=lambda: str(uuid4()))
    title: str
    description: str = ""
    status: TaskStatus = TaskStatus.todo
    due_date: Optional[date] = None
    tags: list[str] = Field(default_factory=list)
