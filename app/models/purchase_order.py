import enum
from datetime import datetime
from app.extensions import db
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, ForeignKey

class POStatus(enum.Enum):
    PENDING = "pending"
    PARTIAL = "partial"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class PurchaseOrder(db.Model):
    __tablename__ = "purchase_orders"

    id: Mapped[int] = mapped_column(primary_key=True, init=False)
    po_number: Mapped[str] = mapped_column(String(50), nullable=False)
    eta: Mapped[datetime] = mapped_column(nullable=False)
    warehouse_id: Mapped[int] = mapped_column(
        ForeignKey("warehouses.id"), nullable=False
    )
    warehouse: Mapped["Warehouse"] = relationship(
        "Warehouse", lazy="select", init=False
    )
    items: Mapped[list] = relationship(
        "PurchaseOrderItem",
        back_populates="purchase_order",
        lazy="selectin",
        init=False,
        cascade="all, delete-orphan",
    )
    status = db.Column(
        db.Enum(POStatus), 
        default=POStatus.PENDING,
        nullable=False
    )
    version = db.Column(db.Integer, nullable=False)

    __mapper_args__ = {"version_id_col": version}

    def __repr__(self):
        return f"<PurchaseOrder {self.po_number} eta:{self.eta}>"
