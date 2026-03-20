from functools import wraps
from flask import request
from flask_jwt_extended import verify_jwt_in_request, get_jwt
from app.models import RolePermission
from app.utils.exceptions import ForbiddenError


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
