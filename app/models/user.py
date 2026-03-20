from typing import Optional
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String
from werkzeug.security import generate_password_hash, check_password_hash
from app.extensions import db
from app.models.user_role import user_roles
from flask_jwt_extended import create_access_token


class User(db.Model):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, init=False)
    username: Mapped[str] = mapped_column(
        String(64), unique=True, index=True, nullable=False
    )
    password_hash: Mapped[Optional[str]] = mapped_column(
        String(128), nullable=False, default=None
    )
    roles: Mapped[list] = relationship(
        "Role",
        secondary=user_roles,
        lazy="subquery",
        collection_class=list,
        backref=db.backref("users", lazy=True),
        init=False,
    )

    @property
    def password(self):
        raise AttributeError("Passpassword is not a readable attribute")

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        if self.password_hash is None:
            return False
        return check_password_hash(self.password_hash, password)

    def create_access_token(self):
        return create_access_token(identity=str(self.id), 
                            additional_claims={"roles": [r.id for r in self.roles]})

    def __repr__(self):
        return f"<User {self.username}>"
