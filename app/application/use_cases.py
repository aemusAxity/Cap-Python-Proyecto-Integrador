from typing import Any, Dict, List

from app.application.ports import OrderRepository
from app.domain.models import Order, OrderItem


class OrderUseCase:
    def __init__(self, repository: OrderRepository):
        self.repository = repository

    def create_new_order(
        self, customer_email: str, items_data: List[Dict[str, Any]]
    ) -> Order:
        # Convertir a entidades de dominio (Dispara las validaciones de negocio)
        items = [
            OrderItem(
                product_name=item["product_name"],
                price=item["price"],
                quantity=item["quantity"],
            )
            for item in items_data
        ]

        # Creación de la Entidad Principal
        new_order = Order(customer_email=customer_email, items=items)

        # Persistencia mediante el puerto abstracto
        saved_order = self.repository.create_order(new_order)

        return saved_order

    def get_order(self, order_id: int) -> Order | None:
        return self.repository.get_order_by_id(order_id)

    def list_orders(self) -> List[Order]:
        return self.repository.get_all_orders()
