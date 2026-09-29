from typing import List, Optional

from sqlalchemy.orm import Session

from app.application.ports import OrderRepository
from app.domain.models import Order, OrderItem
from app.infrastructure.orm_models import OrderItemModel, OrderModel


class SQLAlchemyOrderRepository(OrderRepository):
    def __init__(self, session: Session):
        self.session = session

    def create_order(self, order: Order) -> Order:
        # Entidad de Dominio a Modelo ORM
        db_items = [
            OrderItemModel(
                product_name=item.product_name, price=item.price, quantity=item.quantity
            )
            for item in order.items
        ]

        db_order = OrderModel(
            customer_email=order.customer_email, status=order.status, items=db_items
        )

        self.session.add(db_order)
        self.session.commit()
        self.session.refresh(db_order)

        # Devolver la orden con su nuevo ID generado por la BD
        order.id = db_order.id  # type: ignore
        return order

    def get_order_by_id(self, order_id: int) -> Optional[Order]:
        # 1. Buscar en BD
        db_order = (
            self.session.query(OrderModel).filter(OrderModel.id == order_id).first()
        )
        if not db_order:
            return None

        # Traducir de ORM a Entidad de Dominio
        domain_items = [
            OrderItem(
                product_name=item.product_name, price=item.price, quantity=item.quantity
            )
            for item in db_order.items
        ]

        return Order(
            id=db_order.id,  # type: ignore
            customer_email=db_order.customer_email,  # type: ignore
            status=db_order.status,  # type: ignore
            created_at=db_order.created_at,  # type: ignore
            items=domain_items,  # type: ignore
        )

    def get_all_orders(self) -> List[Order]:
        db_orders = self.session.query(OrderModel).all()
        result = []
        for db_order in db_orders:
            domain_items = [
                OrderItem(
                    product_name=item.product_name,  # type: ignore
                    price=item.price,  # type: ignore
                    quantity=item.quantity,  # type: ignore
                )
                for item in db_order.items
            ]
            result.append(
                Order(
                    id=db_order.id,  # type: ignore
                    customer_email=db_order.customer_email,  # type: ignore
                    status=db_order.status,  # type: ignore
                    created_at=db_order.created_at,  # type: ignore
                    items=domain_items,  # type: ignore
                )
            )
        return result

    def update_order_status(self, order_id: int, new_status: str) -> Order | None:
        # Buscar en BD
        db_order = (
            self.session.query(OrderModel).filter(OrderModel.id == order_id).first()
        )
        if not db_order:
            return None

        db_order.status = new_status  # type: ignore
        self.session.commit()
        self.session.refresh(db_order)

        # 3. Retornar la entidad de Dominio actualizada
        domain_items = [
            OrderItem(
                product_name=item.product_name, price=item.price, quantity=item.quantity
            )
            for item in db_order.items
        ]

        return Order(
            id=db_order.id,  # type: ignore
            customer_email=db_order.customer_email,  # type: ignore
            status=db_order.status,  # type: ignore
            created_at=db_order.created_at,  # type: ignore
            items=domain_items,  # type: ignore
        )

    def delete_order(self, order_id: int) -> bool:
        db_order = (
            self.session.query(OrderModel).filter(OrderModel.id == order_id).first()
        )
        if not db_order:
            return False  # No existía

        self.session.delete(db_order)
        self.session.commit()

        return True
