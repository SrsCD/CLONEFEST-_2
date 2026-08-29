"""
Import every model module here so its table registers on Base.metadata.

This is what makes `from app.models import *` (or just importing this
package) enough for Alembic autogenerate and `Base.metadata.create_all()`
to see the full schema.
"""
from app.models.user import User
from app.models.project import Project, ProjectMember
from app.models.component import Component
from app.models.version import Version
from app.models.milestone import Milestone
from app.models.label import Label, bug_labels
from app.models.bug import Bug
from app.models.comment import Comment
from app.models.attachment import Attachment
from app.models.history import BugHistory
from app.models.relationship import BugRelationship
from app.models.notification import Notification

__all__ = [
    "User",
    "Project",
    "ProjectMember",
    "Component",
    "Version",
    "Milestone",
    "Label",
    "bug_labels",
    "Bug",
    "Comment",
    "Attachment",
    "BugHistory",
    "BugRelationship",
    "Notification",
]
