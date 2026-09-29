from datetime import datetime
from typing import List

from pydantic import BaseModel, ConfigDict, EmailStr, field_serializer


# Request
class ItemCreate(BaseModel):
    product_name: str
    price: float
    quantity: int


class OrderCreate(BaseModel):
    customer_email: EmailStr
    items: List[ItemCreate]


class OrderStatusUpdate(BaseModel):
    status: str


# Response
class ItemResponse(BaseModel):
    product_name: str
    price: float
    quantity: int
    subtotal: float


class OrderResponse(BaseModel):
    id: int
    customer_email: str
    status: str
    total_amount: float
    created_at: datetime
    items: List[ItemResponse]

    @field_serializer("created_at")
    def format_date(self, dt: datetime, _info) -> str:
        return dt.strftime("%d/%m/%Y %H:%M:%S")

    model_config = ConfigDict(from_attributes=True)
