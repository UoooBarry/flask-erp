from functools import wraps
from flask import request
from flask_jwt_extended import verify_jwt_in_request, get_jwt
from app.models import RolePermission
from app.utils.exceptions import ForbiddenError
from sqlalchemy.orm.exc import StaleDataError
from app import db
import time


def permission_required():
    def wrapper(fn):
        @wraps(fn)
        def decorated_view(*args, **kwargs):
            verify_jwt_in_request()
            claims = get_jwt()
            user_role_ids = claims.get("roles", [])

            has_permission = RolePermission.query.filter(
                RolePermission.role_id.in_(user_role_ids),
                RolePermission.blueprint == (request.blueprint or ""),
                RolePermission.endpoint == request.endpoint,
                RolePermission.method == request.method.upper()
            ).first()

            if not has_permission:
                raise ForbiddenError("Permission denied")

            return fn(*args, **kwargs)

        return decorated_view

    return wrapper

def retry_on_concurrency(max_retries=3, delay=0.1):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except StaleDataError as e:
                    db.session.rollback()
                    last_exception = e
                    time.sleep(delay)
            if last_exception:
                raise last_exception
        return wrapper
    return decorator
