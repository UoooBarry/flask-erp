from app.extensions import db
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String


class Role(db.Model):
    __tablename__ = "roles"

    id: Mapped[int] = mapped_column(primary_key=True, init=False)
    name: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)

    def __repr__(self):
        return f"<Role {self.name}>"
