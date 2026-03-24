from app.extensions import db
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, ForeignKey


class Stock(db.Model):
    __tablename__ = "stocks"

    id: Mapped[int] = mapped_column(primary_key=True, init=False)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), nullable=False)
    warehouse_id: Mapped[int] = mapped_column(
        ForeignKey("warehouses.id"), nullable=False
    )
    quantity: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    product: Mapped["Product"] = relationship(
        "Product", back_populates="stocks", lazy="select", init=False
    )
    warehouse: Mapped["Warehouse"] = relationship(
        "Warehouse", back_populates="stocks", lazy="select", init=False
    )
    version = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f"<Stock product_id={self.product_id} warehouse_id={self.warehouse_id} qty={self.quantity}>"

    __table_args__ = (
        db.Index("ix_product_warehouse_lookup", "product_id", "warehouse_id"),
        db.UniqueConstraint("product_id", "warehouse_id", name="uq_product_warehouse"),
    )

    __mapper_args__ = {"version_id_col": version}
