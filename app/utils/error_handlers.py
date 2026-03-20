import logging
from sqlalchemy.exc import IntegrityError, StatementError
from flask import jsonify
from app.utils.exceptions import (
    APIError,
    ValidationError,
    NotFoundError,
    UnauthorizedError,
    ForbiddenError,
    InternalServerError
)
from app.utils.response import render_error

logger = logging.getLogger(__name__)


def register_error_handlers(app):
    @app.errorhandler(APIError)
    def handle_api_error(error):
        return render_error(error.message, error.status_code, error.to_dict())

    @app.errorhandler(IntegrityError)
    def handle_integrity_error(error):
        logger.error(f"Database integrity error: {error}")
        return render_error(
            "Data validation failed",
            422,
            {"database_error": str(error.orig) if error.orig else "Constraint violation"}
        )

    @app.errorhandler(StatementError)
    def handle_statement_error(error):
        logger.error(f"Database statement error: {error}")
        return render_error(
            "Invalid data provided",
            422,
            {"database_error": str(error)}
        )

    @app.errorhandler(404)
    def handle_not_found(error):
        return render_error("Resource not found", 404)

    @app.errorhandler(405)
    def handle_method_not_allowed(error):
        return render_error("Method not allowed", 405)

    @app.errorhandler(500)
    def handle_internal_error(error):
        logger.error(f"Internal server error: {error}", exc_info=True)
        return render_error("Internal server error", 500)

    @app.errorhandler(Exception)
    def handle_unexpected_error(error):
        logger.error(f"Unexpected error: {error}", exc_info=True)
        return render_error("An unexpected error occurred", 500)
