from typing import Optional
from app.extensions import db
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, ForeignKey, Numeric


class PurchaseOrderItem(db.Model):
    __tablename__ = "purchase_order_items"

    id: Mapped[int] = mapped_column(primary_key=True, init=False)
    purchase_order_id: Mapped[int] = mapped_column(
        ForeignKey("purchase_orders.id"), nullable=False
    )
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    received_quantity: Mapped[int] = mapped_column(Integer, nullable=False, default=0, init=False)
    unit_price: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    purchase_order: Mapped["PurchaseOrder"] = relationship(
        "PurchaseOrder", back_populates="items", lazy="select", init=False
    )
    product: Mapped["Product"] = relationship("Product", lazy="select", init=False)
    version = db.Column(db.Integer, nullable=False)

    __mapper_args__ = {"version_id_col": version}

    def __repr__(self):
        return f"<PurchaseOrderItem id={self.id} po_id={self.purchase_order_id} product_id={self.product_id}>"


