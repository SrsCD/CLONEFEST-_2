# BugOff — Core Backend Progress & Handoff

**Owner:** Person 2 (Core Backend) — Shreenidhi
**Status as of:** Aug 29, 2026 — feature-complete for submission
**Stack:** Python + FastAPI + PostgreSQL + SQLAlchemy + Alembic
**Runs locally on:** `http://127.0.0.1:8000`

---

## 1. What's done

Everything in the original Person 2 scope is built and tested (16
automated pytest tests + manual end-to-end smoke tests — not just
code that parses).

| Area | Status |
|---|---|
| Database models (12 tables + enums) | ✅ Done |
| User & project management APIs | ✅ Done |
| Bug CRUD — full field set | ✅ Done |
| Bug lifecycle / status workflow | ✅ Done — server-enforced state machine |
| Comments & attachments | ✅ Done — real file upload |
| Complete bug history / audit log | ✅ Done — auto-logged, no manual calls needed |
| Search & filtering | ✅ Done — combinable query params |
| Labels, components, classification data | ✅ Done |
| Bug relationships (blocks/duplicate/etc.) | ✅ Done |
| Notifications backend | ✅ Done — auto-created on assign/resolve/comment |
| Basic statistics APIs | ✅ Done |
| API layer + docs | ✅ Done — live Swagger at `/docs` |
| Validation & error handling | ✅ Done — 400/403/404/409 used consistently |
| Backend testing | ✅ Done — 16 pytest tests, all passing |

---

## 2. How to run this locally

```bash
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env            # edit DATABASE_URL to match your Postgres
alembic upgrade head
python -m app.seed              # optional sample data
uvicorn app.main:app --reload --port 8000
```

Then open **http://127.0.0.1:8000/docs** — full interactive API, every
endpoint testable in the browser.

Seeded login (if you ran the seed script): `alice` / `bob` / `carol`,
all with password `password123`.

Run tests: `pytest -v` (16 tests, covers auth, permissions, bug
lifecycle, history logging, comments, relationships).

---

## 3. API surface — what's live right now

- **Auth:** `POST /auth/register`, `POST /auth/login`
- **Users:** `GET/PUT /users/me`, `GET /users/{id}`
- **Projects:** full CRUD + members/roles at `/projects` and `/projects/{id}/members`
- **Components/Versions/Milestones:** CRUD under `/projects/{id}/...`
- **Bugs:** `POST/GET /bugs?project_id=`, `GET/PUT/DELETE /bugs/{id}`,
  `GET /bugs/search?...` with combinable filters
- **Comments/Attachments:** `/bugs/{id}/comments`, `/bugs/{id}/attachments`
- **History:** `GET /bugs/{id}/history`
- **Labels:** `/projects/{id}/labels`, assign via `/bugs/{id}/labels/{label_id}`
- **Relationships:** `/bugs/{id}/dependencies` (this is what feeds Jeet's
  dependency-intelligence and blast-radius features)
- **Notifications:** `/notifications`
- **Stats:** `/projects/{id}/stats`

Full request/response shapes are in Swagger (`/docs`) — that's the
source of truth, not this file.

---

## 4. What Jeet's AI service needs from this backend (per his PROGRESS.md)

- ✅ **Fixed Aug 29** — his `schemas.py` assumed field names `component`
  and `reporter` (text), but this API originally returned only
  `component_id`/`reporter_id` (integers). `BugOut` now includes
  resolved text alongside the IDs: `component_name`,
  `reporter_username`, `assignee_username` — real values, not mock.
  Real sample response from a live run:

  ```json
  {
    "id": 1, "project_id": 1,
    "title": "Login fails on mobile Safari",
    "description": "Users can't log in from iOS Safari",
    "reporter_id": 1, "assignee_id": 2,
    "severity": "high", "priority": "p2", "status": "new",
    "component_id": 1, "version_id": null, "milestone_id": null,
    "labels": [],
    "reporter_username": "alice",
    "assignee_username": "bob",
    "component_name": "Authentication"
  }
  ```

  **Open question for Jeet:** confirm `component_name`/`reporter_username`
  match what his classifier expects, or tell us what shape he actually needs.

- ✅ Bug relationships — `GET /bugs/{id}/dependencies` returns
  `{bug_id, outgoing: [...], incoming: [...]}`, real data (not mock)
  once relationships exist via `POST /bugs/{id}/dependencies`
- ✅ Developer/user data — `GET /users/{id}` returns real `skills`;
  component ownership is on `Component.owner_id` — also real, not mock,
  as long as his service calls this running API rather than its own
  hardcoded dataset
- ⬜ **Still open:** how his service actually receives data — simplest
  for tonight is his service polling this REST API directly (no new
  infra needed on either side) rather than a webhook or shared DB
  access. Needs a 2-minute confirmation with Jeet, not more building.

## 5. What Person 3 (frontend) needs to know

- API base URL: `http://127.0.0.1:8000` (or wherever this is deployed)
- Auth: `POST /auth/login` (OAuth2 password form — `username` + `password`
  fields, not JSON) returns a bearer token; send it as
  `Authorization: Bearer <token>` on every other request
- Every endpoint, request/response shape, and example payload is live
  and testable at `/docs`

## 6. What Person 4 (integration/security) needs to know

- JWT auth is implemented (`python-jose`), tokens expire in 60 min by
  default (`ACCESS_TOKEN_EXPIRE_MINUTES` in `.env`)
- CORS is currently open (`allow_origins` from `.env`, defaults to
  localhost dev ports) — tighten for any real deployment
- Role-based access control (viewer/reporter/developer/admin) is
  enforced project-by-project via `require_project_role` /
  `check_membership` in `app/core/deps.py` — worth a look if doing a
  security review
- File uploads are stored on local disk under `uploads/` — fine for a
  demo, would need S3/equivalent for production

---

## 7. Honest limitations (good to know before the demo)

- Attachment storage is local disk, not cloud — fine for tonight, not
  production-ready
- No rate limiting anywhere
- Notification delivery is DB-only (no email/push) — Person 3 would
  poll `GET /notifications`
- Data sync with Jeet's AI service isn't wired up yet — see section 4
- Built and tested fast against a deadline, so edge-case coverage is
  solid but not exhaustive (16 tests cover the core paths, not every
  permutation)

---

## 8. Future work (good talking points for judges, not needed tonight)

- Webhook or polling integration with the AI intelligence service
- Cloud file storage for attachments
- Email/push notification delivery
- Rate limiting and stricter CORS for production
