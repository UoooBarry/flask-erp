from typing import Optional
from app.extensions import db
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, ForeignKey


class InboundItem(db.Model):
    __tablename__ = "inbound_items"

    id: Mapped[int] = mapped_column(primary_key=True, init=False)
    inbound_order_id: Mapped[int] = mapped_column(
        ForeignKey("inbound_orders.id"), nullable=False
    )
    purchase_order_item_id: Mapped[int] = mapped_column(
        ForeignKey("purchase_order_items.id"), nullable=False
    )
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    inbound_order: Mapped["InboundOrder"] = relationship(
        "InboundOrder", back_populates="items", lazy="select", init=False
    )
    purchase_order_item: Mapped["PurchaseOrderItem"] = relationship(
        "PurchaseOrderItem", lazy="select", init=False
    )

    def __repr__(self):
        return f"<InboundItem id={self.id} io_id={self.inbound_order_id} poi_id={self.purchase_order_item_id} qty={self.quantity}>"
