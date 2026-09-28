from sqlalchemy.orm import Session

from app.domain.models import Order, OrderItem
from app.infrastructure.repositories import SQLAlchemyOrderRepository


def test_repository_creates_and_retrieves_order(db_session: Session) -> None:
    # Instanciamos el repositorio real pasándole la BD en memoria
    repo = SQLAlchemyOrderRepository(session=db_session)

    item = OrderItem(product_name="Monitor", price=300.0, quantity=2)
    nueva_orden = Order(customer_email="test@example.com", items=[item])

    # Ejecutamos el SQL INSERT
    orden_guardada = repo.create_order(nueva_orden)

    assert orden_guardada.id is not None

    # Ejecutamos el SQL SELECT
    orden_recuperada = repo.get_order_by_id(orden_guardada.id)

    assert orden_recuperada is not None
    assert orden_recuperada.customer_email == "test@example.com"
    assert len(orden_recuperada.items) == 1
    assert orden_recuperada.items[0].product_name == "Monitor"


def test_repository_updates_order_status(db_session: Session) -> None:
    repo = SQLAlchemyOrderRepository(session=db_session)

    # Insertar orden base
    orden = Order(customer_email="update@db.com", items=[OrderItem("Mouse", 50.0, 1)])
    orden_guardada = repo.create_order(orden)

    # Ejecutar SQL UPDATE
    assert orden_guardada.id is not None
    orden_actualizada = repo.update_order_status(orden_guardada.id, "PAGADO")

    assert orden_actualizada is not None
    assert orden_actualizada.status == "PAGADO"

    verificacion = repo.get_order_by_id(orden_guardada.id)
    assert verificacion is not None
    assert verificacion.status == "PAGADO"


def test_repository_deletes_order(db_session: Session) -> None:
    repo = SQLAlchemyOrderRepository(session=db_session)

    orden = Order(
        customer_email="test@example.com", items=[OrderItem("Teclado", 100.0, 1)]
    )
    orden_guardada = repo.create_order(orden)

    assert orden_guardada.id is not None
    # Ejecutar SQL DELETE
    resultado = repo.delete_order(orden_guardada.id)

    assert resultado is True
    assert repo.get_order_by_id(orden_guardada.id) is None


def test_repository_get_all_orders(db_session: Session) -> None:
    repo = SQLAlchemyOrderRepository(session=db_session)

    orden1 = Order(
        customer_email="test1@example.com", items=[OrderItem("Mouse", 50.0, 1)]
    )
    orden2 = Order(
        customer_email="test2@example.com", items=[OrderItem("Teclado", 100.0, 1)]
    )

    repo.create_order(orden1)
    repo.create_order(orden2)

    # Ejecutamos el SQL SELECT múltiple
    todas_las_ordenes = repo.get_all_orders()

    assert len(todas_las_ordenes) == 2

    correos = [orden.customer_email for orden in todas_las_ordenes]
    assert "test1@example.com" in correos
    assert "test2@example.com" in correos


def test_repository_fails_when_updating_non_existent_order(db_session: Session) -> None:
    repo = SQLAlchemyOrderRepository(session=db_session)

    resultado = repo.update_order_status(9999, "PAGADO")

    assert resultado is None


def test_repository_fails_when_deleting_non_existent_order(db_session: Session) -> None:
    repo = SQLAlchemyOrderRepository(session=db_session)

    resultado = repo.delete_order(9999)

    assert resultado is False
