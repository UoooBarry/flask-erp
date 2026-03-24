from typing import Any, Optional
from flask import jsonify


def render_success(
        data: Any = None, status_code: int = 200, meta_data: dict | None = None
) -> tuple[dict, int]:
    response = {
        "success": True,
        "data": data,
        "meta": meta_data or {},
    }

    if data is not None:
        response["data"] = data

    return jsonify(response), status_code


def render_error(
    message: str, status_code: int, errors: Optional[dict] = None
) -> tuple[dict, int]:
    response = {"success": False, "message": message}

    if errors:
        response["errors"] = errors

    return jsonify(response), status_code
