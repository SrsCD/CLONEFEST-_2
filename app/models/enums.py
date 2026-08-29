"""
Shared enums used across models.

Kept in one place so the same vocabulary (status names, roles, etc.)
is used consistently in models, schemas, and business logic — and so
Jeet's AI service can be told these exact string values once and stay
in sync.
"""
import enum


class BugSeverity(str, enum.Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    TRIVIAL = "trivial"


class BugPriority(str, enum.Enum):
    P0 = "p0"  # drop everything
    P1 = "p1"  # urgent
    P2 = "p2"  # normal
    P3 = "p3"  # low
    P4 = "p4"  # backlog


class BugStatus(str, enum.Enum):
    NEW = "new"
    CONFIRMED = "confirmed"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    VERIFIED = "verified"
    CLOSED = "closed"
    REOPENED = "reopened"


# The only transitions the lifecycle logic (Phase 5) will allow.
# Kept here so it lives next to the enum it governs.
ALLOWED_STATUS_TRANSITIONS: dict[BugStatus, set[BugStatus]] = {
    BugStatus.NEW: {BugStatus.CONFIRMED, BugStatus.CLOSED},
    BugStatus.CONFIRMED: {BugStatus.IN_PROGRESS, BugStatus.CLOSED},
    BugStatus.IN_PROGRESS: {BugStatus.RESOLVED, BugStatus.CONFIRMED},
    BugStatus.RESOLVED: {BugStatus.VERIFIED, BugStatus.REOPENED},
    BugStatus.VERIFIED: {BugStatus.CLOSED, BugStatus.REOPENED},
    BugStatus.CLOSED: {BugStatus.REOPENED},
    BugStatus.REOPENED: {BugStatus.CONFIRMED, BugStatus.IN_PROGRESS},
}


class ProjectRole(str, enum.Enum):
    ADMIN = "admin"
    DEVELOPER = "developer"
    REPORTER = "reporter"
    VIEWER = "viewer"


class RelationshipType(str, enum.Enum):
    DUPLICATE_OF = "duplicate_of"
    BLOCKS = "blocks"
    BLOCKED_BY = "blocked_by"
    RELATED_TO = "related_to"
    DEPENDS_ON = "depends_on"


class NotificationType(str, enum.Enum):
    ASSIGNED = "assigned"
    STATUS_CHANGED = "status_changed"
    COMMENTED = "commented"
    REOPENED = "reopened"
    RESOLVED = "resolved"
    MENTIONED = "mentioned"
    PROJECT_ACTIVITY = "project_activity"


class HistoryActionType(str, enum.Enum):
    CREATED = "created"
    STATUS_CHANGED = "status_changed"
    PRIORITY_CHANGED = "priority_changed"
    SEVERITY_CHANGED = "severity_changed"
    ASSIGNEE_CHANGED = "assignee_changed"
    COMMENT_ADDED = "comment_added"
    ATTACHMENT_ADDED = "attachment_added"
    LABEL_CHANGED = "label_changed"
    REOPENED = "reopened"
    RELATIONSHIP_ADDED = "relationship_added"
