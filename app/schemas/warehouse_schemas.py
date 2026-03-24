from pydantic import BaseModel, field_validator, model_validator, ConfigDict
from typing import Optional


class WarehouseCreate(BaseModel):
    name: Optional[str] = None
    location: Optional[str] = None

    @model_validator(mode='after')
    def validate_name(self):
        if not self.name:
            raise ValueError("Warehouse name is required")
        return self

    model_config = ConfigDict(extra='allow')


class WarehouseUpdate(BaseModel):
    name: Optional[str] = None
    location: Optional[str] = None

    @model_validator(mode='after')
    def validate_name(self):
        if self.name is not None and not self.name:
            raise ValueError("Warehouse name cannot be empty")
        return self

    model_config = ConfigDict(extra='allow')


class WarehouseResponse(BaseModel):
    id: int
    name: str
    location: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
