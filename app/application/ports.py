from abc import ABC, abstractmethod
from typing import List, Optional

from app.domain.models import Order


class OrderRepository(ABC):
    @abstractmethod
    def create_order(self, order: Order) -> Order:
        pass  # pragma: no cover

    @abstractmethod
    def get_order_by_id(self, order_id: int) -> Optional[Order]:
        pass  # pragma: no cover

    @abstractmethod
    def get_all_orders(self) -> List[Order]:
        pass  # pragma: no cover

    @abstractmethod
    def update_order_status(self, order_id: int, new_status: str) -> Optional[Order]:
        pass  # pragma: no cover

    @abstractmethod
    def delete_order(self, order_id: int) -> bool:
        pass  # pragma: no cover
