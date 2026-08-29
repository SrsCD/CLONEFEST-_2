# BugOff — Core Backend (Person 2)

FastAPI + PostgreSQL backend for a modern bug-tracking platform.

**Status: feature-complete for submission.** Auth, projects, bugs,
lifecycle, comments, attachments, history, search, labels,
relationships, notifications, and stats are all built and tested
(16 automated tests, all passing, plus manual end-to-end smoke tests).

## Prerequisites

- Python 3.11 or 3.12 (see note below if you're on 3.14)
- PostgreSQL 14+ (or Docker)
- VS Code with the Python extension

## Setup

```bash
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# edit .env — set DATABASE_URL, and set SECRET_KEY to something random
```

### Postgres via Docker (simplest)
```bash
docker run --name issueforge-pg -e POSTGRES_USER=bugzilla_user \
  -e POSTGRES_PASSWORD=bugzilla_pass -e POSTGRES_DB=bugzilla_db \
  -p 5432:5432 -d postgres:16
```
(Or install Postgres natively and create a matching user/db — see
`.env.example` for the exact values expected.)

### Python 3.14 compatibility
This project targets Python 3.11-3.14. Two dependency pins in
`requirements.txt` exist specifically for 3.14 support:
- `sqlalchemy>=2.0.45,<2.1` — earlier 2.0.x releases crash on 3.14 with
  a `TypeError` in ORM model definitions (fixed starting 2.0.41,
  refined further in 2.0.44/2.0.45)
- `psycopg[binary]>=3.2.10,<4` instead of `psycopg2-binary`, which has
  no 3.14 wheels

If a fresh `pip install -r requirements.txt` ever fails again, it's
almost always one dependency lacking a wheel for whatever Python
version you're on — `pip install --upgrade pip` first, or fall back to
Python 3.12 for the widest wheel coverage.

## Run it

```bash
alembic upgrade head       # creates all tables
python -m app.seed         # optional: sample data (users alice/bob/carol, password123)
uvicorn app.main:app --reload --port 8000
```

Swagger docs: http://127.0.0.1:8000/docs — this is the full, live API
contract for Person 3 (frontend) and Person 4 (integration) to build
against, testable directly in the browser.

## Run the tests

```bash
pytest -v
```

16 tests covering auth, project permissions, bug lifecycle, history
logging, comments, and relationships.

## VS Code setup

1. Open this folder in VS Code.
2. Install the Python extension if needed.
3. `Ctrl+Shift+P` → "Python: Select Interpreter" → `./venv/bin/python`.
4. Open a terminal (auto-activates the venv) and run the commands above.

## What's built

### Auth & Users
- `POST /auth/register`, `POST /auth/login` (JWT bearer tokens)
- `GET/PUT /users/me`, `GET /users/{id}`

### Projects
- `POST/GET /projects`, `GET/PUT/DELETE /projects/{id}` (delete = archive)
- Members: `GET/POST /projects/{id}/members`, `PUT/DELETE /projects/{id}/members/{user_id}`
- Role-based access: viewer < reporter < developer < admin, enforced on every route

### Components / Versions / Milestones
- Full CRUD under `/projects/{id}/components|versions|milestones`

### Bugs — the core
- `POST/GET /bugs?project_id=`, `GET/PUT/DELETE /bugs/{id}`
- `GET /bugs/search?project_id=&status=&severity=&priority=&assignee_id=&reporter_id=&component_id=&version_id=&milestone_id=&is_security=&q=` — all filters combinable
- Full field set: title, description, reporter, assignee, severity,
  priority, status, component, version, milestone, environment, repro
  steps, expected/actual behavior, due date, is_security

### Lifecycle
- Status state machine enforced server-side (`app/models/enums.py` →
  `ALLOWED_STATUS_TRANSITIONS`): New → Confirmed → In Progress →
  Resolved → Verified → Closed, with Reopen from Resolved/Verified/Closed
- Invalid transitions rejected with 400
- `resolved_at`/`closed_at` auto-stamped

### Comments & Attachments
- `GET/POST /bugs/{id}/comments`, `PUT/DELETE /bugs/{id}/comments/{id}` (author-only edit/delete, or project admin)
- `GET/POST/DELETE /bugs/{id}/attachments` (files stored under `uploads/{bug_id}/`)

### History / Audit log
- `GET /bugs/{id}/history` — every status/priority/severity/assignee
  change, comment, attachment, label, and relationship change is logged
  automatically, no manual calls needed in route handlers

### Labels & Relationships
- Labels: `GET/POST /projects/{id}/labels`, `PUT/DELETE .../labels/{id}`
- Assign to bug: `POST/DELETE /bugs/{id}/labels/{label_id}`
- Relationships (duplicate_of, blocks, blocked_by, related_to, depends_on):
  `POST /bugs/{id}/dependencies`, `GET /bugs/{id}/dependencies` (outgoing + incoming),
  `DELETE /bugs/{id}/dependencies/{relationship_id}`
- **This is what Jeet's AI service needs** for dependency intelligence
  and blast-radius — the `GET .../dependencies` response shape is
  exactly `{bug_id, outgoing: [...], incoming: [...]}`

### Notifications
- `GET /notifications?unread_only=`, `PUT /notifications/{id}/read`, `PUT /notifications/read-all`
- Auto-created on: assignment, bug resolved, new comment

### Statistics
- `GET /projects/{id}/stats` → total/open/closed counts, breakdowns by
  status/severity/priority/component/assignee — raw data for Person 3's
  dashboard charts

### Validation & errors
- 404 for missing resources, 403 for permission failures, 409 for
  conflicts (duplicate username/email/project key/component/label
  name), 400 for invalid status transitions — consistent across every
  router

## What Jeet's service needs from you (per his PROGRESS.md)

- Bug field names: confirmed — `title`, `description`, `component_id`
  (not `component`), `reporter_id`, `assignee_id` (see `BugOut` in
  `app/schemas/bug.py` for the exact contract)
- Bug relationships: `GET /bugs/{id}/dependencies` returns exactly
  `blocks`-style data — see above
- Developer/user data: `GET /users/{id}` returns `skills` (comma
  string) — component ownership is on `Component.owner_id`
- Data sync: not yet decided — simplest for tonight is Jeet's service
  polling this API directly using the endpoints above

## Project layout

```
app/
  main.py, config.py, database.py, seed.py
  models/       12 SQLAlchemy models + enums.py + common.py (all Phase 2)
  schemas/      Pydantic request/response schemas, one file per resource
  routers/      auth, users, projects, components, versions, milestones,
                bugs (CRUD/lifecycle/comments/attachments/labels/relationships/history),
                labels, notifications, stats
  core/         security.py (JWT/hashing), deps.py (auth + role checks), exceptions.py
alembic/        migrations (initial schema included, verified against models)
tests/          16 pytest tests covering auth, permissions, bugs, lifecycle, history
uploads/        attachment file storage (gitignored except .gitkeep)
```
