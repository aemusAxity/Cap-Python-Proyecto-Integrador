from abc import ABC, abstractmethod
from typing import List, Optional

from app.domain.models import Order


class OrderRepository(ABC):
    @abstractmethod
    def create_order(self, order: Order) -> Order:
        pass

    @abstractmethod
    def get_order_by_id(self, order_id: int) -> Optional[Order]:
        pass

    @abstractmethod
    def get_all_orders(self) -> List[Order]:
        pass
