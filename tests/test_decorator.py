import pytest
from app import create_app
from app.utils.decorator import permission_required


@pytest.fixture
def app_with_permission_route():
    app = create_app('testing')
    
    @app.route('/test-protected', methods=['GET'])
    @permission_required()
    def protected_view():
        return {"msg": "success"}, 200
    
    @app.route('/test-protected-no-roles', methods=['GET'])
    @permission_required()
    def protected_view_no_roles():
        return {"msg": "success"}, 200
    
    return app


class TestPermissionDecorator:
    def test_decorator_denies_access_without_permission(self, app_with_permission_route, db):
        from app.models import Role, User

        with app_with_permission_route.app_context():
            role = Role(name="user")
            db.session.add(role)
            db.session.commit()

            user = User(username="testuser")
            user.password = "password"
            user.roles.append(role)
            db.session.add(user)
            db.session.commit()

            token = user.create_access_token()

        with app_with_permission_route.test_client() as client:
            response = client.get('/test-protected', headers={"Authorization": f"Bearer {token}"})
            data = response.get_json()
            
            assert response.status_code == 403
            assert data["success"] is False
            assert data["message"] == "Permission denied"

    def test_decorator_denies_access_with_no_roles(self, app_with_permission_route, db):
        from app.models import Role, User

        with app_with_permission_route.app_context():
            role = Role(name="user")
            db.session.add(role)
            db.session.commit()

            user = User(username="testuser")
            user.roles.append(role)
            user.password = "password"
            db.session.add(user)
            db.session.commit()

            token = user.create_access_token()

        with app_with_permission_route.test_client() as client:
            response = client.get('/test-protected-no-roles', headers={"Authorization": f"Bearer {token}"})
            data = response.get_json()
            
            assert response.status_code == 403
            assert data["success"] is False

