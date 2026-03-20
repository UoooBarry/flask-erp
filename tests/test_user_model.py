import pytest
from datetime import datetime, timezone
from sqlalchemy.exc import IntegrityError
from app.models.user import User


class TestUserModel:
    
    def test_user_creation(self, db):
        user = User(username='testuser')
        user.password = 'password123'
        db.session.add(user)
        db.session.commit()
        
        assert user.id is not None
        assert user.username == 'testuser'
        assert user.password_hash is not None
        assert user.password_hash != 'password123'

    def test_password_hashing(self, db):
        user = User(username='testuser')
        user.password = 'password123'
        
        assert user.password_hash is not None
        assert user.password_hash != 'password123'
        assert len(user.password_hash) > 0

    def test_check_password_correct(self, db):
        user = User(username='testuser')
        user.password = 'password123'
        
        assert user.check_password('password123') is True

    def test_check_password_incorrect(self, db):
        user = User(username='testuser')
        user.password = 'password123'
        
        assert user.check_password('wrongpassword') is False

    def test_password_property_raises_error(self, db):
        user = User(username='testuser')
        user.password = 'password123'
        
        with pytest.raises(AttributeError):
            _ = user.password

    def test_username_unique_constraint(self, db):
        user1 = User(username='testuser')
        user1.password = 'password123'
        db.session.add(user1)
        db.session.commit()
        
        user2 = User(username='testuser')
        user2.password = 'password456'
        db.session.add(user2)
        
        with pytest.raises(IntegrityError):
            db.session.commit()

    def test_username_nullable_constraint(self, db):
        user = User(username='testuser')
        user.password_hash = None  # Clear the password hash to simulate missing password
        db.session.add(user)
        
        with pytest.raises(IntegrityError):
            db.session.commit()

    def test_password_nullable_constraint(self, db):
        user = User(username='testuser')
        db.session.add(user)
        
        with pytest.raises(IntegrityError):
            db.session.commit()

    def test_created_at_timestamp(self, db):
        user = User(username='testuser')
        user.password = 'password123'
        db.session.add(user)
        db.session.commit()
        
        assert user.created_at is not None
        assert isinstance(user.created_at, datetime)

    def test_updated_at_timestamp(self, db):
        user = User(username='testuser')
        user.password = 'password123'
        db.session.add(user)
        db.session.commit()
        
        original_updated_at = user.updated_at
        
        user.username = 'updateduser'
        db.session.commit()
        
        assert user.updated_at is not None
        assert isinstance(user.updated_at, datetime)
        assert user.updated_at >= original_updated_at

    def test_repr_method(self, db):
        user = User(username='testuser')
        user.password = 'password123'
        
        assert repr(user) == '<User testuser>'

    def test_password_update(self, db):
        user = User(username='testuser')
        user.password = 'oldpassword'
        db.session.add(user)
        db.session.commit()
        
        old_hash = user.password_hash
        
        user.password = 'newpassword'
        db.session.commit()
        
        assert user.password_hash != old_hash
        assert user.check_password('newpassword') is True
        assert user.check_password('oldpassword') is False

    def test_user_query_by_username(self, db):
        user = User(username='testuser')
        user.password = 'password123'
        db.session.add(user)
        db.session.commit()
        
        found_user = User.query.filter_by(username='testuser').first()
        
        assert found_user is not None
        assert found_user.username == 'testuser'
        assert found_user.id == user.id

    def test_user_query_by_id(self, db):
        user = User(username='testuser')
        user.password = 'password123'
        db.session.add(user)
        db.session.commit()
        
        found_user = db.session.get(User, user.id)
        
        assert found_user is not None
        assert found_user.username == 'testuser'

    def test_user_delete(self, db):
        user = User(username='testuser')
        user.password = 'password123'
        db.session.add(user)
        db.session.commit()
        
        user_id = user.id
        
        db.session.delete(user)
        db.session.commit()
        
        found_user = db.session.get(User, user_id)
        assert found_user is None

    def test_username_max_length(self, db):
        user = User(username='a' * 64)
        user.password = 'password123'
        db.session.add(user)
        db.session.commit()
        
        assert user.username == 'a' * 64

    def test_multiple_users(self, db):
        users = []
        for i in range(5):
            user = User(username=f'user{i}')
            user.password = f'password{i}'
            users.append(user)
        
        for user in users:
            db.session.add(user)
        db.session.commit()
        
        all_users = User.query.all()
        assert len(all_users) == 5
        assert all(u.username.startswith('user') for u in all_users)
