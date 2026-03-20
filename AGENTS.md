# AGENTS.md

This file contains guidelines for agentic coding assistants working on this Flask ERP project.

## Project Overview

Flask-based ERP system using SQLAlchemy 2.0+ with dataclass-style models, JWT authentication, and role-based access control.

## Commands

### Development
- **Run app**: `flask run` or `python run.py`
- **Seed database**: `python seeds.py`
- **Database migrations**: `flask db migrate` / `flask db upgrade`

### Testing
- **Run all tests**: `pytest`
- **Run specific test file**: `pytest tests/test_user_model.py`
- **Run single test**: `pytest tests/test_user_model.py::TestUserModel::test_user_creation`
- **Run with coverage**: `pytest --cov=app`

## Code Style Guidelines

### Imports
- Use relative imports within the `app` package: `from app.models import User`, `from app.extensions import db`
- Standard library imports first, then third-party, then local imports
- Import specific classes/functions rather than entire modules when possible
- Blank line between import groups

### Formatting
- 4 spaces indentation (no tabs)
- 2 blank lines between top-level definitions (classes, functions)
- Max line length: ~100 characters
- No trailing whitespace
- Newline at end of file

### Types
- Use SQLAlchemy 2.0+ `Mapped` type hints: `id: Mapped[int] = mapped_column(primary_key=True, init=False)`
- Use `Optional` for nullable fields: `password_hash: Mapped[Optional[str]]`
- All model classes inherit from `db.Model` which uses `MappedAsDataclass` and `DeclarativeBase`
- Use type hints for function parameters and return values

### Naming Conventions
- Classes: `PascalCase` (`User`, `Role`, `Config`)
- Functions/methods: `snake_case` (`check_password`, `create_access_token`)
- Variables: `snake_case` (`username`, `password_hash`)
- Database tables: `plural_snake_case` (`users`, `roles`, `user_roles`)
- Model attributes: `snake_case`
- Blueprint names: `snake_case` (`auth_bp`)
- Private methods: use underscore prefix if needed

### Database/ORM Patterns
- All models must define `__tablename__`
- Use `init=False` for auto-generated fields (primary keys, timestamps)
- Use relationships with proper lazy loading: `lazy="subquery"` or `lazy=True`
- Use backref for reverse relationships
- Commit explicitly after modifications: `db.session.commit()`
- Use `db.session.get(Model, id)` for single object queries
- Use `Model.query.filter_by(field=value).first()` for filtered queries

### Flask/Blueprint Structure
- Register routes in Blueprints under `app/routes/`
- Blueprints registered in `app/__init__.py` with URL prefix
- Blueprint pattern: `bp_name = Blueprint('bp_name', __name__)`
- Route decorators: `@bp_name.route('/path', methods=['POST', 'GET'])`

### Error Handling
- Raise `AttributeError` for read-only properties accessed directly
- Use `IntegrityError` for database constraint violations in tests
- API errors return JSON with HTTP status codes: `return jsonify({"msg": "error"}), 401`
- Test exceptions with `pytest.raises(ExceptionType)`

### Testing
- Use pytest framework with fixtures in `tests/conftest.py`
- Test classes named `Test<ClassName>` (e.g., `TestUserModel`)
- Test methods named `test_<what_is_tested>` (e.g., `test_password_hashing`)
- Use fixtures: `app`, `db`, `new_user`
- Test both happy path and error cases
- Use assertions to validate expected behavior

### Security
- Never store plain text passwords - use `generate_password_hash()` and `check_password_hash()`
- Use JWT tokens for authentication via `flask_jwt_extended`
- Store secrets in environment variables (`.env` file, loaded via `python-dotenv`)
- Use `@permission_required()` decorator for protected routes

### Configuration
- Config classes in `config.py`: `Config`, `DevelopmentConfig`, `TestingConfig`, `ProductionConfig`
- Environment-based config selection: `create_app('development' | 'testing' | 'production')`
- Database URIs configured per environment (development uses `data.db`, testing uses `test.db`)

### Timestamps
- Base model in `app/extensions.py` provides `created_at` and `updated_at`
- `created_at`: auto-generated on creation (UTC)
- `updated_at`: auto-updated on modification (UTC)

### General Patterns
- Use `__repr__` methods for models: `return f"<User {self.username}>"`
- Use @property with @setter for sensitive fields like passwords
- Keep routes thin - business logic in models or utils
- Use Flask's `jsonify()` for JSON responses
- Import all models in `app/models/__init__.py` for convenience
