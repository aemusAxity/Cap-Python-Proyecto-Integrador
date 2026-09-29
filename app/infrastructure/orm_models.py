from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.infrastructure.database import Base


class OrderModel(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    customer_email = Column(String, nullable=False)
    status = Column(String, default="PENDING")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relación uno a muchos con OrderItemModel
    items = relationship(
        "OrderItemModel", back_populates="order", cascade="all, delete-orphan"
    )


class OrderItemModel(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"))
    product_name = Column(String, nullable=False)
    price = Column(Float, nullable=False)
    quantity = Column(Integer, nullable=False)

    order = relationship("OrderModel", back_populates="items")
