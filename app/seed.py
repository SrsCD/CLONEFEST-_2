"""
Seed the database with sample data for local development / demo.

Run with:
    python -m app.seed

Safe to re-run: it checks for existing data first and skips instead of
duplicating.
"""
from datetime import date, timedelta

from passlib.context import CryptContext

from app.database import SessionLocal, Base, engine
from app.models import (
    User,
    Project,
    ProjectMember,
    Component,
    Version,
    Milestone,
    Label,
    Bug,
    Comment,
    BugHistory,
    BugRelationship,
)
from app.models.enums import (
    ProjectRole,
    BugSeverity,
    BugPriority,
    BugStatus,
    RelationshipType,
    HistoryActionType,
)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def seed() -> None:
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        if db.query(User).first() is not None:
            print("Database already has data — skipping seed.")
            return

        # --- Users ---
        alice = User(
            username="alice",
            email="alice@example.com",
            hashed_password=pwd_context.hash("password123"),
            full_name="Alice Sharma",
            skills="auth,security,python",
        )
        bob = User(
            username="bob",
            email="bob@example.com",
            hashed_password=pwd_context.hash("password123"),
            full_name="Bob Iyer",
            skills="frontend,react,ui",
        )
        carol = User(
            username="carol",
            email="carol@example.com",
            hashed_password=pwd_context.hash("password123"),
            full_name="Carol Mehta",
            skills="database,backend,python",
        )
        db.add_all([alice, bob, carol])
        db.flush()  # get IDs without committing yet

        # --- Project ---
        project = Project(name="BugOff Demo", key="BO", description="Sample project for local dev")
        db.add(project)
        db.flush()

        db.add_all(
            [
                ProjectMember(project_id=project.id, user_id=alice.id, role=ProjectRole.ADMIN),
                ProjectMember(project_id=project.id, user_id=bob.id, role=ProjectRole.DEVELOPER),
                ProjectMember(project_id=project.id, user_id=carol.id, role=ProjectRole.DEVELOPER),
            ]
        )

        # --- Components / Versions / Milestones / Labels ---
        auth_component = Component(
            project_id=project.id, name="Authentication", owner_id=alice.id,
            description="Login, tokens, sessions",
        )
        ui_component = Component(
            project_id=project.id, name="Frontend UI", owner_id=bob.id,
            description="React components and pages",
        )
        db.add_all([auth_component, ui_component])

        v1 = Version(project_id=project.id, name="v1.0.0", release_date=date.today() - timedelta(days=30), is_released=True)
        v2 = Version(project_id=project.id, name="v1.1.0", is_released=False)
        db.add_all([v1, v2])

        milestone = Milestone(project_id=project.id, name="Beta Launch", due_date=date.today() + timedelta(days=14))
        db.add(milestone)

        label_bug = Label(project_id=project.id, name="bug", color="#d73a4a")
        label_security = Label(project_id=project.id, name="security", color="#b60205")
        db.add_all([label_bug, label_security])
        db.flush()

        # --- Bugs ---
        bug1 = Bug(
            project_id=project.id,
            title="Login fails with valid credentials on mobile Safari",
            description="Users report login fails intermittently on iOS Safari.",
            reporter_id=carol.id,
            assignee_id=alice.id,
            severity=BugSeverity.HIGH,
            priority=BugPriority.P1,
            status=BugStatus.IN_PROGRESS,
            component_id=auth_component.id,
            version_id=v1.id,
            milestone_id=milestone.id,
            environment="iOS 18, Safari",
            reproduction_steps="1. Open app on iOS Safari\n2. Enter valid credentials\n3. Tap login",
            expected_behavior="User is logged in and redirected to dashboard",
            actual_behavior="Spinner hangs, then session expired error",
            is_security=False,
        )
        bug2 = Bug(
            project_id=project.id,
            title="Token refresh endpoint accepts expired refresh tokens",
            description="Refresh token validation does not check expiry correctly.",
            reporter_id=alice.id,
            assignee_id=alice.id,
            severity=BugSeverity.CRITICAL,
            priority=BugPriority.P0,
            status=BugStatus.CONFIRMED,
            component_id=auth_component.id,
            version_id=v1.id,
            is_security=True,
        )
        bug3 = Bug(
            project_id=project.id,
            title="Dashboard chart overflows on small screens",
            description="Chart component breaks layout below 400px width.",
            reporter_id=bob.id,
            severity=BugSeverity.LOW,
            priority=BugPriority.P3,
            status=BugStatus.NEW,
            component_id=ui_component.id,
            version_id=v2.id,
        )
        db.add_all([bug1, bug2, bug3])
        db.flush()

        bug1.labels.append(label_bug)
        bug2.labels.append(label_bug)
        bug2.labels.append(label_security)

        # --- Comments ---
        db.add(Comment(bug_id=bug1.id, author_id=alice.id, content="Can reproduce on iOS 18.1, investigating token flow."))
        db.add(Comment(bug_id=bug2.id, author_id=carol.id, content="This looks related to bug1 — same token code path."))

        # --- Relationship (used by Jeet's dependency intelligence) ---
        db.add(
            BugRelationship(
                bug_id=bug2.id,
                related_bug_id=bug1.id,
                relationship_type=RelationshipType.BLOCKS,
                created_by_id=alice.id,
                note="Fix the expiry check before the Safari session bug can be verified.",
            )
        )

        # --- History entries ---
        db.add(
            BugHistory(
                bug_id=bug1.id, changed_by_id=carol.id, action_type=HistoryActionType.CREATED,
            )
        )
        db.add(
            BugHistory(
                bug_id=bug1.id, changed_by_id=alice.id, action_type=HistoryActionType.STATUS_CHANGED,
                field_name="status", old_value="new", new_value="in_progress",
            )
        )

        db.commit()
        print("Seeded: 3 users, 1 project, 2 components, 3 bugs, comments, 1 relationship, history.")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
