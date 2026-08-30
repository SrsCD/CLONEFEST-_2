# BugOff — Core Backend 

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

# CLONEFEST-_2 
BugSight 
Modern Intelligent Bug Tracking Platform
BugSight is a modern, intelligent bug tracking and issue management platform, built as a ground-up reconstruction of the developer workflow problem originally addressed by Bugzilla.

Rather than replicating Bugzilla's legacy UI or architecture, BugSight rethinks the entire experience — from how bugs are reported and triaged, to how teams understand why bugs keep happening. It is built on a contemporary technology stack with a clean, intuitive interface, structured collaboration workflows, and a layer of explainable AI intelligence that turns raw bug data into actionable developer insight.

The reference implementation (Bugzilla) was studied to understand the core workflows: bug lifecycle management, component ownership, user access control, flag/attachment handling, search, and reporting. BugSight preserves the essential capabilities of these workflows while reimagining every aspect of the user experience, architecture, and intelligence layer.

Core Capabilities
Create, assign, track, and resolve bugs across a full software development lifecycle
Component and product-based organisation
Role-based access control and user management
Attachment and flag support
Advanced search and filtering
Activity history and audit trails
Reporting and analytics dashboards
Email notification workflows

Our Innovations
1. Explainable Intelligent Bug Triage

When a bug is submitted, the system automatically determines its severity, priority, category, and component — and crucially, explains its reasoning. Instead of a black-box classification, the developer sees: "Classified as Critical because: the affected component is authentication, the description mentions data exposure, and similar past bugs in this module were escalated." Transparency builds trust in automation.

2. Explainable Duplicate Detection

Before a bug is saved, the system scans for potential duplicates and surfaces them with similarity scores and explanations: "91% match with Bug #421 — both reference the same component, similar error message, and comparable reproduction steps." This reduces noise in the tracker without silently suppressing reports.

3. Intelligent Bug Assignment

Rather than assigning bugs by workload alone, the system recommends the best-suited developer based on expertise, component ownership, code familiarity, and history of resolving similar bugs. Workload is shown as context, not used as the primary decision factor. This means bugs reach the right person faster.

4. Dependency Intelligence

Instead of simply displaying a dependency chain (Bug A → Bug B → Bug C), the system performs actual decision support: "Bug A is currently blocking 7 other issues — resolving it first will unblock the most work." The platform surfaces root blockers and helps teams prioritise intelligently.

5. Bug Stagnation Intelligence

The system detects bugs that are becoming problematic and explains exactly why they are stuck. Rather than just showing "open for 31 days", it tells the team: "No assignee, no activity in 14 days, missing reproduction steps, and blocked by an unresolved dependency." Both detection and explanation are provided, enabling teams to take targeted action on stalled issues.

6. Security Bug Mode with Vulnerability Workflow

Bugs can be marked as Security Vulnerabilities, triggering automatic visibility restrictions — only the security team, assigned developer, and project administrators can view the report. Beyond access control, the platform introduces a dedicated security workflow with fields for CVSS score, affected component, exploitability level, disclosure status, and remediation deadline. This transforms security bug handling from simple restricted access into a structured, auditable vulnerability management process.

7. Bug → Code Intelligence

The platform connects Bug → Component → Files → Commits → Developer → Fix into a coherent intelligence graph. This allows the system to surface insights such as: "The authentication module has generated 18 bugs across the last 3 releases" or "This component has had 4 security vulnerabilities." Developers and engineering leads gain genuine visibility into which parts of the codebase need structural attention.

8. Bug Pattern and Root-Cause Intelligence

Given a large volume of bugs, the system identifies recurring patterns and probable root areas. For example, across 500 bugs, it may surface: "38 bugs are related to authentication — 21 involve token handling — 15 occurred after changes to the same module. Recurring problem detected in /auth/token_manager: 15 historical bugs, 4 security bugs, 6 reopened." This shifts the team's thinking from fixing bugs to understanding why bugs keep being produced — a fundamentally more valuable capability.

9. Predictive Bug Detection — Catch Bugs Before They Happen

By analysing code changes alongside historical bug patterns, the platform identifies high-risk changes before they cause failures: "This authentication change closely resembles previous changes that introduced regressions — consider validating token handling before merging." Critically, analysis runs locally inside the company's environment — only metadata and results are sent to the platform, never source code. This makes the feature viable even for security-sensitive organisations.

10. Bug Genealogy — Find the Bug That Keeps Coming Back

Some bugs are reported, fixed, closed — and then quietly reappear months later as a different ticket. BugSight builds a Bug Genealogy that links recurring manifestations of the same underlying problem across time, allowing the team to recognise repeat offenders rather than treating each recurrence as a fresh, unrelated issue.

11. Bug Blast Radius — Know What Breaks If You Don't Fix It

For any open bug, the system analyses dependencies and relationships to calculate and visualise its blast radius: "This authentication bug potentially impacts 4 components, 3 critical workflows, and 12 existing bugs — estimated affected functionality: High." When the bug is fixed, the blast radius updates to zero. This gives teams a clear, quantified answer to the question: "How urgent is this, really?"

Technology Stack



Getting Started


