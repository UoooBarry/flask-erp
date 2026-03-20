from app.extensions import db
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import ForeignKey


class RolePermission(db.Model):
    __tablename__ = "role_permissions"

    id: Mapped[int] = mapped_column(primary_key=True, init=False)
    role_id: Mapped[int] = mapped_column(ForeignKey('roles.id'), nullable=False)
    blueprint: Mapped[str]
    endpoint: Mapped[str]
    method: Mapped[str]

    __table_args__ = (
        db.Index("ix_role_permissions_lookup", "role_id", "blueprint", "endpoint", "method"),
    )
