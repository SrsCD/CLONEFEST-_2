"""
Small custom exceptions mapped to HTTP responses in main.py's exception
handlers (Phase 11 will expand on this). For now routers mostly raise
HTTPException directly, but these cover the couple of cases reused
across multiple routers.
"""
from fastapi import HTTPException, status


class NotFoundError(HTTPException):
    def __init__(self, detail: str = "Resource not found"):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail)


class ForbiddenError(HTTPException):
    def __init__(self, detail: str = "You don't have permission to do this"):
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail=detail)


class ConflictError(HTTPException):
    def __init__(self, detail: str = "Conflict with existing resource"):
        super().__init__(status_code=status.HTTP_409_CONFLICT, detail=detail)
