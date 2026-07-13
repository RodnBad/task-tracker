# Task Tracker

A task management API with a Kanban board frontend, built with FastAPI and vanilla JavaScript.

**Course:** AUB AI-Assisted Coding  
**Submission branch:** `mid-course-project`

---

## Features
- CRUD for tasks (create, read, update, delete)
- Status transitions: `todo → in_progress → done` (or revert to `todo`)
- **Feature A — Due dates:** optional due date per task, `?overdue=true` filter
- **Feature B — Tags:** list of string labels per task, `?tag=<label>` filter
- Filters are combinable: `?overdue=true&tag=bug`
- Kanban board frontend with drag-and-drop, create/edit modal, live filters

---

## Quick Start

### 1. Install dependencies
```bash
pip install -r requirements-dev.txt
```

### 2. Run the API
```bash
uvicorn app.main:app --reload
```
API available at `http://localhost:8000`  
Interactive docs at `http://localhost:8000/docs`

### 3. Open the frontend
Open `frontend/index.html` in your browser (no build step required).

---

## Running Tests
```bash
pytest -v
```
Expected: 43 tests, all passing.

---

## API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Health check |
| POST | `/tasks` | Create task |
| GET | `/tasks` | List tasks (supports `?overdue=true` and `?tag=<label>`) |
| GET | `/tasks/{id}` | Get task by ID |
| PUT | `/tasks/{id}` | Update task |
| DELETE | `/tasks/{id}` | Delete task |

### Example: Create a task
```bash
curl -X POST http://localhost:8000/tasks \
  -H "Content-Type: application/json" \
  -d '{"title":"Fix login bug","due_date":"2026-07-20","tags":["bug","urgent"]}'
```

### Example: Get overdue tasks tagged "bug"
```bash
curl "http://localhost:8000/tasks?overdue=true&tag=bug"
```

---

## Docker
```bash
docker build -t task-tracker .
docker run -p 8000:8000 task-tracker
```

---

## Project Structure
```
app/               # FastAPI application
frontend/          # Kanban board (single HTML file)
tests/             # pytest test suite
docs/midcourse/    # Mid-course project documentation
.github/workflows/ # CI pipeline
```
