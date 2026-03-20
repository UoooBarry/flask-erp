import pytest
from app import create_app
from app.extensions import db as _db

@pytest.fixture(scope='session')
def app():
    app = create_app('testing')
    return app

@pytest.fixture
def db(app):
    with app.app_context():
        _db.create_all()
        yield _db
        _db.session.remove()
        _db.drop_all()

@pytest.fixture
def new_user(db):
    from app.models.user import User
    user = User(username='test_admin')
    user.password = 'secure_password'
    return user
