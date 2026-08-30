# BugOff

### Modern Bug Tracking & Developer Intelligence Platform

BugOff is a modern bug tracking and developer intelligence platform inspired by the core workflow of Bugzilla.

Instead of treating a bug as just a ticket that needs to be assigned and closed, BugOff provides additional context around an issue why it may be happening, whether it has appeared before, who is best suited to work on it, what other issues it may affect, and whether similar problems are recurring in the project.

The project is built around two independent backend services: a **Core Bug Tracking System** and an **AI & Developer Intelligence Service**.

---

## Key Innovations

### 1. Predictive Risk Detection

Identifies potentially risky code changes before they introduce bugs by comparing changes against historical bug and regression patterns.

The analysis is designed to run locally so that proprietary source code does not have to leave the development environment.

### 2. Bug Genealogy

Connects newly reported bugs with previously resolved bugs that may share similar symptoms or an underlying cause.

This helps teams identify recurring problems instead of treating every recurrence as a completely new issue.

### 3. Dynamic Blast Radius Analysis

Determines the potential impact of an unresolved bug across related bugs, components, and workflows.

The analysis also reflects how the impact changes as issues are resolved.

### 4. Explainable Bug Triage

Automatically suggests:

- Severity
- Priority
- Category
- Component

Each recommendation includes a plain-language explanation of the signals that contributed to it.

### 5. Intelligent Developer Assignment

Recommends the developer best suited to work on a bug based primarily on:

- Component ownership
- Relevant expertise
- Previous fixes
- Experience in the affected area

Workload is considered as context rather than being the primary assignment criterion.

### 6. Explainable Duplicate Detection

Identifies potentially duplicate bugs using:

- TF-IDF
- Cosine similarity
- Optional semantic matching

The results include similarity scores and the terms or signals contributing to the match.

### 7. Dependency Intelligence

Analyzes relationships between bugs to identify:

- Root blockers
- Dependency chains
- Critical dependencies
- Circular dependencies

Instead of simply showing linked issues, the system identifies which issues should be addressed first.

### 8. Bug Stagnation Intelligence

Identifies why a bug may be stuck, including:

- No recent activity
- No assignee
- Unresolved blockers
- Missing reproduction information
- Repeated reopening

### 9. Pattern & Root-Cause Intelligence

Groups recurring issues by component and shared vocabulary to identify parts of a system that repeatedly generate defects.

This shifts the focus from simply fixing individual bugs toward understanding recurring problem areas.

### 10. Bug → Code Intelligence

Uses available bug history and code-related metadata to identify components and files that have repeatedly been associated with defects across releases.

---

## Core Bug Tracking

The Core Backend provides the complete bug tracking workflow required by a development team.

### User & Project Management

- User registration and login
- JWT authentication
- Project creation and management
- Project membership
- Project-level role-based access
- Components
- Versions
- Milestones

### Bug Management

BugOff supports complete bug management, including:

- Create, view, update and delete bugs
- Severity
- Priority
- Status
- Component
- Version
- Milestone
- Environment
- Reproduction steps
- Expected behaviour
- Actual behaviour
- Labels
- Reporter
- Assignee

### Bug Lifecycle

The backend enforces the following lifecycle:

`New → Confirmed → In Progress → Resolved → Verified → Closed`

Reopening is also supported, and invalid state transitions are rejected by the server.

### Comments & Attachments

Users can:

- Add and manage comments
- Upload bug-related files
- Attach screenshots, logs and other evidence to issues

### Search & Filtering

Bugs can be searched and filtered using multiple fields, including:

- Status
- Severity
- Priority
- Assignee
- Reporter
- Component
- Version
- Labels
- Milestone
- Date
- Bug ID
- Text content

Filters can also be combined.

### Bug Relationships

BugOff supports relationships such as:

- Blocks
- Blocked By
- Depends On
- Duplicate Of
- Related To

These relationships provide the foundation for the dependency and blast-radius analysis performed by the Intelligence Service.

---

## Audit Trail

Every meaningful change to a bug is automatically recorded in the bug history.

This includes:

- Status changes
- Priority changes
- Severity changes
- Assignee changes
- Comments
- Attachments
- Labels
- Relationships

This provides a complete history of how an issue evolved without requiring developers to manually create audit entries.

---

## Access Control

Authentication is implemented using **JWT**.

Project-level Role-Based Access Control is provided through four roles:

| Role | Access |
|------|--------|
| Viewer | View project and bug information |
| Reporter | Report and interact with issues |
| Developer | Work on assigned issues and development workflows |
| Admin | Manage project-level settings and members |

Permissions are enforced at the API level so that access rules remain consistent throughout the system.

---

## Architecture

BugOff uses a **decoupled microservice architecture**.

The system consists of:

| Service | Responsibility |
|---------|----------------|
| Core Bug System | Users, projects, bugs, workflow, relationships, history and notifications |
| Intelligence Service | AI/XAI analysis, duplicate detection, assignment, dependencies, genealogy, prediction and impact analysis |
| Frontend | User interface, dashboards and visualization |
| Integration & Security Layer | API integration, testing, security validation and deployment |

The Core Bug System and Intelligence Service communicate through REST APIs.

This separation allows both services to be developed and tested independently.

---

## Intelligence Service Architecture

The Intelligence Service separates HTTP handling from analytical logic.

FastAPI routers are responsible for handling API requests and Pydantic is used for request and response validation.

The actual analytical algorithms are maintained separately in logic modules.

This structure makes individual intelligence features:

- Easier to test
- Easier to maintain
- Independent from HTTP routing
- Replaceable without changing the entire service

---

## Intelligence Pipeline

BugOff follows a **deterministic-first intelligence approach**.

Analytical methods such as similarity scoring and graph traversal first generate the underlying results.

The Anthropic Claude API is then used in a constrained role to convert these grounded results into clear, human-readable explanations rather than allowing unrestricted model reasoning.

This approach keeps the explanations tied to the actual signals produced by the system.

---

## Technology Stack

### Core Backend

- Python 3.11+
- FastAPI
- PostgreSQL
- SQLAlchemy
- Alembic
- Pydantic

### AI & Developer Intelligence

- Python
- FastAPI
- Pydantic
- scikit-learn
- TF-IDF
- Cosine Similarity
- NetworkX
- Anthropic Claude API

### Authentication

- JWT
- Role-Based Access Control

---

## Database

The Core Backend is built around 12 relational models:

1. Users
2. Projects
3. Project Members
4. Bugs
5. Comments
6. Attachments
7. Components
8. Versions
9. Milestones
10. Bug History
11. Bug Relationships
12. Notifications

SQLAlchemy is used for database interaction and Alembic is used for database migrations.

---

## API

Both backend services expose REST APIs through FastAPI.

The APIs are documented through FastAPI's built-in **Swagger UI**, allowing endpoints to be inspected and tested during development.

The Intelligence Service provides 10 implemented endpoints covering:

- Explainable triage
- Duplicate detection
- Intelligent assignment
- Dependency analysis
- Bug stagnation
- Bug-to-code analysis
- Pattern detection
- Predictive risk
- Bug genealogy
- Blast-radius analysis

---

## Testing

### Core Backend

The Core Backend includes **16 automated tests** covering:

- Authentication
- Permission enforcement
- Bug lifecycle transitions
- History logging

### Intelligence Service

All 10 intelligence endpoints have been implemented and tested end-to-end using realistic mock data involving:

- Authentication bugs
- Export-related bugs
- Cross-component dependencies

The Intelligence Service is currently prepared to consume live data from the Core Bug System once the required data interfaces are connected.

---

## Project Structure

The project is organized into separate frontend, core backend, and intelligence service components.

```text
BugOff/
│
├── frontend/
│
├── core-backend/
│   ├── app/
│   ├── models/
│   ├── routers/
│   ├── services/
│   ├── migrations/
│   └── tests/
│
├── intelligence-service/
│   ├── routers/
│   ├── schemas/
│   ├── *_logic.py
│   └── tests/
│
└── docs/
```

The backend services are independently structured so that core bug management and intelligence features can be developed and tested without tightly coupling their implementations.

---

## Project Workflow

The overall workflow can be summarized as:

**Report → Store → Analyze → Assign → Understand Impact → Fix → Verify → Learn**

A typical issue can move through the following process:

1. A user reports a bug through the frontend.
2. The Core Backend validates and stores the issue.
3. The Intelligence Service analyzes the bug.
4. The system provides triage, duplicate, assignment and dependency insights.
5. The potential impact and related issues are identified.
6. A suitable developer works on the issue.
7. The bug is resolved and verified.
8. The complete activity is recorded in the audit history.
9. Historical data can be used for future analysis and predictions.

---

## Why BugOff?

Traditional bug trackers mainly answer:

> **What is broken?**

BugOff tries to answer a broader set of questions:

- Is this bug likely to be a duplicate?
- Why was this severity or priority suggested?
- Who has the most relevant experience to fix it?
- Is another bug blocking this one?
- What could be affected if it remains unresolved?
- Has a similar problem appeared before?
- Which parts of the system repeatedly generate defects?
- Could a planned change introduce a regression?

The goal is not to replace the developer's decision-making, but to give developers more useful information when making those decisions.

---

## Future Scope

Potential extensions include:

- GitHub and GitLab integration
- CI/CD integration
- Security vulnerability workflows
- Local code-risk analyzers
- More advanced project analytics
- Enterprise and on-premise deployment

---

## Team

BugOff was developed as a team project for the **CloneFest Developer Tool Reconstruction — Bugzilla** track.

The project focuses on taking the core problem addressed by Bugzilla and rebuilding it as a modern, explainable and intelligence-driven developer tool.
 
