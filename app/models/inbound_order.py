import enum
from datetime import datetime
from app.extensions import db
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, ForeignKey


class InboundStatus(enum.Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class InboundOrder(db.Model):
    __tablename__ = "inbound_orders"

    id: Mapped[int] = mapped_column(primary_key=True, init=False)
    purchase_order_id: Mapped[int] = mapped_column(
        ForeignKey("purchase_orders.id"), nullable=False
    )
    received_date: Mapped[datetime] = mapped_column(nullable=False)
    notes: Mapped[str] = mapped_column(String(512), nullable=True)
    status = db.Column(
        db.Enum(InboundStatus),
        default=InboundStatus.PENDING,
        nullable=False
    )
    version = db.Column(db.Integer, nullable=False)
    purchase_order: Mapped["PurchaseOrder"] = relationship(
        "PurchaseOrder", lazy="select", init=False
    )
    items: Mapped[list] = relationship(
        "InboundItem",
        back_populates="inbound_order",
        lazy="selectin",
        init=False,
        cascade="all, delete-orphan"
    )

    __mapper_args__ = {"version_id_col": version}

    def __repr__(self):
        return f"<InboundOrder id={self.id} po_id={self.purchase_order_id} status:{self.status}>"
