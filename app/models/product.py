from typing import Optional
from app.extensions import db
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Numeric, Integer, ForeignKey


class Product(db.Model):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(primary_key=True, init=False)
    name: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(String(512))
    sku: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    price: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    stocks: Mapped[list] = relationship(
        "Stock",
        back_populates="product",
        lazy="select",
        init=False
    )

    @property
    def total_quantity(self) -> int:
        return sum(stock.quantity for stock in self.stocks) if self.stocks else 0

    def __repr__(self):
        return f"<Product {self.name} {self.sku}>"
