from typing import Any, Optional


class APIError(Exception):
    def __init__(self, message: str, status_code: int = 500, payload: Optional[dict] = None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.payload = payload or {}

    def to_dict(self) -> dict:
        rv = dict(self.payload or ())
        rv['message'] = self.message
        return rv


class ValidationError(APIError):
    def __init__(self, message: str = "Validation error", payload: Optional[dict] = None):
        super().__init__(message, status_code=422, payload=payload)


class NotFoundError(APIError):
    def __init__(self, message: str = "Resource not found", payload: Optional[dict] = None):
        super().__init__(message, status_code=404, payload=payload)


class UnauthorizedError(APIError):
    def __init__(self, message: str = "Unauthorized", payload: Optional[dict] = None):
        super().__init__(message, status_code=401, payload=payload)


class ForbiddenError(APIError):
    def __init__(self, message: str = "Forbidden", payload: Optional[dict] = None):
        super().__init__(message, status_code=403, payload=payload)


class InternalServerError(APIError):
    def __init__(self, message: str = "Internal server error", payload: Optional[dict] = None):
        super().__init__(message, status_code=500, payload=payload)
