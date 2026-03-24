from pydantic import BaseModel, model_validator, ConfigDict
from typing import Optional, List
from datetime import datetime


class InboundItemCreate(BaseModel):
    purchase_order_item_id: Optional[int] = None
    quantity: Optional[int] = None

    @model_validator(mode='after')
    def validate_fields(self):
        if not self.purchase_order_item_id:
            raise ValueError("Purchase order item ID is required")
        if self.quantity is None:
            raise ValueError("Quantity is required")
        if self.quantity <= 0:
            raise ValueError("Quantity must be greater than 0")
        return self

    model_config = ConfigDict(extra='allow')


class InboundItemReceive(BaseModel):
    sku: Optional[str] = None
    received_qty: Optional[int] = None

    @model_validator(mode='after')
    def validate_fields(self):
        if not self.sku:
            raise ValueError("SKU is required")
        if self.received_qty is None:
            raise ValueError("Received quantity is required")
        if self.received_qty <= 0:
            raise ValueError("Received quantity must be greater than 0")
        return self

    model_config = ConfigDict(extra='allow')


class InboundOrderReceive(BaseModel):
    inbound_order_id: Optional[int] = None
    items: List[InboundItemReceive] = []

    @model_validator(mode='after')
    def validate_fields(self):
        if not self.inbound_order_id:
            raise ValueError("Inbound order ID is required")
        if not self.items:
            raise ValueError("At least one item is required")
        return self

    model_config = ConfigDict(extra='allow')


class InboundItemResponse(BaseModel):
    id: int
    purchase_order_item_id: int
    quantity: int

    model_config = ConfigDict(from_attributes=True)


class InboundOrderCreate(BaseModel):
    purchase_order_id: Optional[int] = None
    received_date: Optional[datetime] = None
    notes: Optional[str] = None
    items: List[InboundItemCreate] = []

    @model_validator(mode='after')
    def validate_fields(self):
        if not self.purchase_order_id:
            raise ValueError("Purchase order ID is required")
        if not self.received_date:
            raise ValueError("Received date is required")
        if not self.items:
            raise ValueError("At least one item is required")
        return self

    model_config = ConfigDict(extra='allow')


class InboundOrderUpdate(BaseModel):
    received_date: Optional[datetime] = None
    notes: Optional[str] = None
    status: Optional[str] = None

    model_config = ConfigDict(extra='allow')


class InboundOrderResponse(BaseModel):
    id: int
    purchase_order_id: int
    received_date: datetime
    notes: Optional[str] = None
    status: str
    items: List[InboundItemResponse] = []

    model_config = ConfigDict(from_attributes=True)


class InboundOrderListResponse(BaseModel):
    id: int
    purchase_order_id: int
    received_date: datetime
    status: str

    model_config = ConfigDict(from_attributes=True)
