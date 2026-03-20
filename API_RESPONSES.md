# API Response and Error Handling

This document describes the unified API response and error handling system for the Flask ERP application.

## Response Helpers

Use the response helpers from `app.utils.response` to create consistent API responses.

### `render_success(data=None, meta_data=None)`

Returns a successful response with HTTP 200 status code.

```python
from app.utils.response import render_success

# Success with data
return render_success({"id": 1, "name": "John"})

# Success with data and meta
return render_success(
    {"id": 1, "name": "John"},
    meta_data={"total": 100, "page": 1}
)

# Success without data
return render_success()
```

### `render_error(message, status_code, errors=None)`

Returns an error response with the specified status code.

```python
from app.utils.response import render_error

# Simple error
return render_error("Not found", 404)

# Error with validation details
return render_error(
    "Validation failed",
    422,
    errors={"email": "Invalid email format"}
)
```

## Custom Exceptions

Use custom exceptions from `app.utils.exceptions` to raise specific errors with proper status codes.

### Available Exceptions

- `ValidationError` (422) - For validation errors
- `NotFoundError` (404) - When a resource is not found
- `UnauthorizedError` (401) - For authentication failures
- `ForbiddenError` (403) - For authorization failures
- `InternalServerError` (500) - For unexpected server errors

### Usage Examples

```python
from app.utils.exceptions import (
    ValidationError,
    NotFoundError,
    UnauthorizedError
)

# Validation error
raise ValidationError("Invalid input data")

# Not found error
raise NotFoundError("User not found")

# Unauthorized error
raise UnauthorizedError("Invalid credentials")

# With custom payload
raise ValidationError(
    "Validation failed",
    payload={"field": "email", "error": "Invalid format"}
)
```

## Database Error Handling

SQLAlchemy database errors are automatically caught and converted to appropriate responses:

- `IntegrityError` - Converted to 422 with "Data validation failed" message
- `StatementError` - Converted to 422 with "Invalid data provided" message

## Example Routes

```python
from flask import Blueprint, request
from app.models import User
from app.utils.response import render_success, render_error
from app.utils.exceptions import ValidationError, NotFoundError

bp = Blueprint('users', __name__)

@bp.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    user = db.session.get(User, user_id)
    if not user:
        raise NotFoundError("User not found")
    
    return render_success({
        "id": user.id,
        "username": user.username
    })

@bp.route('/users', methods=['POST'])
def create_user():
    data = request.get_json()
    
    if not data.get('username'):
        raise ValidationError("Username is required")
    
    try:
        user = User(username=data['username'])
        user.password = data['password']
        db.session.add(user)
        db.session.commit()
        
        return render_success({
            "id": user.id,
            "username": user.username
        }, status_code=201)
    except Exception as e:
        db.session.rollback()
        raise
```

## Automatic Error Handling

All custom exceptions and standard Flask errors are automatically caught and converted to the unified response format by the error handlers registered in `app.utils.error_handlers`.

## Response Format

### Success Response
```json
{
  "success": true,
  "data": { ... },
  "meta": { ... }  // optional
}
```

### Error Response
```json
{
  "success": false,
  "message": "Error message",
  "errors": { ... }  // optional
}
```
