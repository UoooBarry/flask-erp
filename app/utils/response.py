from typing import Any, Optional
from flask import jsonify


def render_success(data: Any = None, meta_data: Optional[dict] = None) -> tuple[dict, int]:
    response = {"success": True}
    
    if data is not None:
        response["data"] = data
    
    if meta_data:
        response["meta"] = meta_data
    
    return jsonify(response), 200


def render_error(message: str, status_code: int, errors: Optional[dict] = None) -> tuple[dict, int]:
    response = {
        "success": False,
        "message": message
    }
    
    if errors:
        response["errors"] = errors
    
    return jsonify(response), status_code
