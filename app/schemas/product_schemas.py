from pydantic import BaseModel, field_validator, model_validator, ConfigDict, ValidationInfo
from typing import Optional, List


class StockInfo(BaseModel):
    warehouse_id: int
    warehouse_name: str
    quantity: int

    model_config = ConfigDict(from_attributes=True)


class ProductCreate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    sku: Optional[str] = None
    price: Optional[float] = None

    @model_validator(mode='after')
    def validate_fields(self):
        if not self.name:
            raise ValueError("Product name is required")
        if not self.sku:
            raise ValueError("Product SKU is required")
        if self.price is None:
            raise ValueError("Product price is required")
        if self.price <= 0:
            raise ValueError("Product price must be greater than 0")
        return self

    model_config = ConfigDict(extra='allow')


class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    sku: Optional[str] = None
    price: Optional[float] = None

    @model_validator(mode='after')
    def validate_fields(self):
        if self.name is not None and not self.name:
            raise ValueError("Product name cannot be empty")
        if self.sku is not None and not self.sku:
            raise ValueError("Product SKU cannot be empty")
        if self.price is not None:
            if self.price <= 0:
                raise ValueError("Product price must be greater than 0")
        return self

    model_config = ConfigDict(extra='allow')


class StockAdd(BaseModel):
    warehouse_id: Optional[int] = None
    quantity: Optional[int] = None

    @model_validator(mode='after')
    def validate_fields(self):
        if not self.warehouse_id:
            raise ValueError("Warehouse ID is required")
        if self.quantity is None:
            raise ValueError("Quantity is required")
        if self.quantity <= 0:
            raise ValueError("Quantity must be greater than 0")
        return self

    model_config = ConfigDict(extra='allow')


class StockUpdate(BaseModel):
    warehouse_id: Optional[int] = None
    quantity: Optional[int] = None

    @model_validator(mode='after')
    def validate_fields(self):
        if not self.warehouse_id:
            raise ValueError("Warehouse ID is required")
        if self.quantity is None:
            raise ValueError("Quantity is required")
        if self.quantity < 0:
            raise ValueError("Quantity cannot be negative")
        return self

    model_config = ConfigDict(extra='allow')


class StockRemove(BaseModel):
    warehouse_id: Optional[int] = None

    @model_validator(mode='after')
    def validate_fields(self):
        if not self.warehouse_id:
            raise ValueError("Warehouse ID is required")
        return self

    model_config = ConfigDict(extra='allow')


class ProductResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    sku: str
    price: float
    total_quantity: int = 0
    stocks: List[StockInfo] = []

    model_config = ConfigDict(from_attributes=True)


class ProductListResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    sku: str
    price: float
    total_quantity: int = 0

    model_config = ConfigDict(from_attributes=True)
