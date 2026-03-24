from pydantic import BaseModel, field_validator, model_validator, ConfigDict
from typing import Optional, List
from datetime import datetime


class PurchaseOrderItemCreate(BaseModel):
    product_id: Optional[int] = None
    quantity: Optional[int] = None
    unit_price: Optional[float] = None

    @model_validator(mode='after')
    def validate_fields(self):
        if not self.product_id:
            raise ValueError("Product ID is required")
        if self.quantity is None:
            raise ValueError("Quantity is required")
        if self.quantity <= 0:
            raise ValueError("Quantity must be greater than 0")
        if self.unit_price is None:
            raise ValueError("Unit price is required")
        if self.unit_price <= 0:
            raise ValueError("Unit price must be greater than 0")
        return self

    model_config = ConfigDict(extra='allow')


class PurchaseOrderItemUpdate(BaseModel):
    product_id: Optional[int] = None
    quantity: Optional[int] = None
    unit_price: Optional[float] = None

    @model_validator(mode='after')
    def validate_fields(self):
        if self.quantity is not None:
            if self.quantity <= 0:
                raise ValueError("Quantity must be greater than 0")
        if self.unit_price is not None:
            if self.unit_price <= 0:
                raise ValueError("Unit price must be greater than 0")
        return self

    model_config = ConfigDict(extra='allow')


class PurchaseOrderItemResponse(BaseModel):
    id: int
    product_id: int
    quantity: int
    unit_price: float

    model_config = ConfigDict(from_attributes=True)


class PurchaseOrderCreate(BaseModel):
    po_number: Optional[str] = None
    eta: Optional[datetime] = None
    warehouse_id: Optional[int] = None
    items: List[PurchaseOrderItemCreate] = []

    @model_validator(mode='after')
    def validate_fields(self):
        if not self.po_number:
            raise ValueError("PO number is required")
        if not self.eta:
            raise ValueError("ETA is required")
        if not self.warehouse_id:
            raise ValueError("Warehouse ID is required")
        if not self.items:
            raise ValueError("At least one item is required")
        return self

    model_config = ConfigDict(extra='allow')


class PurchaseOrderUpdate(BaseModel):
    po_number: Optional[str] = None
    eta: Optional[datetime] = None
    warehouse_id: Optional[int] = None
    items: Optional[List[PurchaseOrderItemUpdate]] = None

    @model_validator(mode='after')
    def validate_fields(self):
        if self.items is not None:
            if not self.items:
                raise ValueError("Items cannot be empty")
        return self

    model_config = ConfigDict(extra='allow')


class PurchaseOrderResponse(BaseModel):
    id: int
    po_number: str
    eta: datetime
    warehouse_id: int
    items: List[PurchaseOrderItemResponse] = []

    model_config = ConfigDict(from_attributes=True)


class PurchaseOrderListResponse(BaseModel):
    id: int
    po_number: str
    eta: datetime
    warehouse_id: int

    model_config = ConfigDict(from_attributes=True)
