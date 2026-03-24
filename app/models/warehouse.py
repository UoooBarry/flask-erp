from typing import Optional
from app.extensions import db
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Integer


class Warehouse(db.Model):
    __tablename__ = "warehouses"

    id: Mapped[int] = mapped_column(primary_key=True, init=False)
    name: Mapped[str] = mapped_column(String(128), unique=True, nullable=False, index=True)
    location: Mapped[Optional[str]] = mapped_column(String(256))
    stocks: Mapped[list] = relationship(
        "Stock",
        back_populates="warehouse",
        lazy="select",
        init=False
    )

    def __repr__(self):
        return f"<Warehouse {self.name}>"
