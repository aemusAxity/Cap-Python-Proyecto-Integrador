from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import List, Optional


@dataclass
class OrderItem:
    product_name: str
    price: float
    quantity: int

    @property
    def subtotal(self) -> float:
        return self.price * self.quantity


@dataclass
class Order:
    id: Optional[int] = None
    customer_email: str = ""
    items: List[OrderItem] = field(default_factory=list)
    status: str = "PENDIENTE"
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __post_init__(self) -> None:
        if not self.items:
            raise ValueError("Una orden debe tener al menos un item")
        if not self.customer_email or "@" not in self.customer_email:
            raise ValueError("Email inválido")

    @property
    def total_amount(self) -> float:
        return sum(item.subtotal for item in self.items)

    def mark_as_paid(self) -> None:
        self.status = "PAGADO"
