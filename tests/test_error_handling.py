import pytest
from app import create_app
from app.utils.exceptions import (
    ValidationError,
    NotFoundError,
    UnauthorizedError,
    ForbiddenError,
    InternalServerError
)


@pytest.fixture
def app_with_routes():
    app = create_app('testing')
    
    @app.route('/test-validation')
    def test_validation():
        raise ValidationError("Invalid data")
    
    @app.route('/test-not-found')
    def test_not_found():
        raise NotFoundError("Resource not found")
    
    @app.route('/test-unauthorized')
    def test_unauthorized():
        raise UnauthorizedError("Unauthorized access")
    
    @app.route('/test-forbidden')
    def test_forbidden():
        raise ForbiddenError("Access forbidden")
    
    @app.route('/test-generic')
    def test_generic():
        raise Exception("Unexpected error")
    
    return app


class TestExceptions:
    def test_validation_error_creation(self):
        error = ValidationError("Invalid input")
        assert error.message == "Invalid input"
        assert error.status_code == 422
        assert error.to_dict() == {"message": "Invalid input"}

    def test_validation_error_with_payload(self):
        error = ValidationError("Invalid input", payload={"field": "username"})
        assert error.message == "Invalid input"
        assert error.to_dict() == {"field": "username", "message": "Invalid input"}

    def test_not_found_error(self):
        error = NotFoundError("User not found")
        assert error.message == "User not found"
        assert error.status_code == 404

    def test_unauthorized_error(self):
        error = UnauthorizedError("Invalid credentials")
        assert error.message == "Invalid credentials"
        assert error.status_code == 401

    def test_forbidden_error(self):
        error = ForbiddenError("Access denied")
        assert error.message == "Access denied"
        assert error.status_code == 403

    def test_internal_server_error(self):
        error = InternalServerError("Something went wrong")
        assert error.message == "Something went wrong"
        assert error.status_code == 500


class TestResponseHelpers:
    def test_render_success_with_data(self, app):
        from app.utils.response import render_success
        
        with app.app_context():
            response, status_code = render_success({"id": 1, "name": "Test"})
            data = response.get_json()
            
            assert status_code == 200
            assert data["success"] is True
            assert data["data"] == {"id": 1, "name": "Test"}

    def test_render_success_with_meta_data(self, app):
        from app.utils.response import render_success
        
        with app.app_context():
            response, status_code = render_success(
                {"id": 1},
                meta_data={"total": 100, "page": 1}
            )
            data = response.get_json()
            
            assert status_code == 200
            assert data["success"] is True
            assert data["data"] == {"id": 1}
            assert data["meta"] == {"total": 100, "page": 1}

    def test_render_success_without_data(self, app):
        from app.utils.response import render_success
        
        with app.app_context():
            response, status_code = render_success()
            data = response.get_json()
            
            assert status_code == 200
            assert data["success"] is True
            assert "data" not in data

    def test_render_error(self, app):
        from app.utils.response import render_error
        
        with app.app_context():
            response, status_code = render_error("Not found", 404)
            data = response.get_json()
            
            assert status_code == 404
            assert data["success"] is False
            assert data["message"] == "Not found"

    def test_render_error_with_errors(self, app):
        from app.utils.response import render_error
        
        with app.app_context():
            response, status_code = render_error(
                "Validation failed",
                422,
                errors={"username": "Username is required"}
            )
            data = response.get_json()
            
            assert status_code == 422
            assert data["success"] is False
            assert data["message"] == "Validation failed"
            assert data["errors"] == {"username": "Username is required"}


class TestErrorHandlers:
    def test_validation_error_handler(self, app_with_routes):
        with app_with_routes.test_client() as client:
            response = client.get('/test-validation')
            data = response.get_json()
            
            assert response.status_code == 422
            assert data["success"] is False
            assert data["message"] == "Invalid data"

    def test_not_found_error_handler(self, app_with_routes):
        with app_with_routes.test_client() as client:
            response = client.get('/test-not-found')
            data = response.get_json()
            
            assert response.status_code == 404
            assert data["success"] is False
            assert data["message"] == "Resource not found"

    def test_unauthorized_error_handler(self, app_with_routes):
        with app_with_routes.test_client() as client:
            response = client.get('/test-unauthorized')
            data = response.get_json()
            
            assert response.status_code == 401
            assert data["success"] is False
            assert data["message"] == "Unauthorized access"

    def test_forbidden_error_handler(self, app_with_routes):
        with app_with_routes.test_client() as client:
            response = client.get('/test-forbidden')
            data = response.get_json()
            
            assert response.status_code == 403
            assert data["success"] is False
            assert data["message"] == "Access forbidden"

    def test_generic_exception_handler(self, app_with_routes):
        with app_with_routes.test_client() as client:
            response = client.get('/test-generic')
            data = response.get_json()
            
            assert response.status_code == 500
            assert data["success"] is False
            assert data["message"] == "An unexpected error occurred"
