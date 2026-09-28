from typing import Any, Dict, List
from unittest.mock import MagicMock

import pytest

from app.application.ports import OrderRepository
from app.application.use_cases import OrderUseCase
from app.domain.models import Order, OrderItem


def test_create_new_order_success_with_mock() -> None:
    mock_repo = MagicMock(spec=OrderRepository)

    item = OrderItem(product_name="Monitor", price=300.0, quantity=2)
    orden_simulada = Order(id=1, customer_email="test@example.com", items=[item])

    mock_repo.create_order.return_value = orden_simulada

    use_case = OrderUseCase(repository=mock_repo)

    items_data = [{"product_name": "Monitor", "price": 300.0, "quantity": 2}]

    order = use_case.create_new_order("test@example.com", items_data)

    assert order.id == 1
    assert order.customer_email == "test@example.com"
    mock_repo.create_order.assert_called_once()

    args, kwargs = mock_repo.create_order.call_args
    orden_enviada_a_guardar = args[0]

    assert isinstance(orden_enviada_a_guardar, Order)
    assert orden_enviada_a_guardar.customer_email == "test@example.com"
    assert len(orden_enviada_a_guardar.items) == 1
    assert orden_enviada_a_guardar.items[0].product_name == "Monitor"


def test_get_order_success_with_mock() -> None:
    mock_repo = MagicMock(spec=OrderRepository)
    item = OrderItem(product_name="Mouse", price=50.0, quantity=1)
    orden_esperada = Order(id=5, customer_email="test@example.com", items=[item])

    mock_repo.get_order_by_id.return_value = orden_esperada

    use_case = OrderUseCase(repository=mock_repo)

    resultado = use_case.get_order(5)

    mock_repo.get_order_by_id.assert_called_once_with(5)
    assert resultado is not None
    assert resultado.id == 5


def test_list_orders_success_with_mock() -> None:
    mock_repo = MagicMock(spec=OrderRepository)

    item = OrderItem(product_name="Teclado", price=100.0, quantity=1)
    lista_esperada = [
        Order(id=1, customer_email="test1@example.com", items=[item]),
        Order(id=2, customer_email="test2@example.com", items=[item]),
    ]
    mock_repo.get_all_orders.return_value = lista_esperada

    use_case = OrderUseCase(repository=mock_repo)

    resultados = use_case.list_orders()

    mock_repo.get_all_orders.assert_called_once()
    assert len(resultados) == 2
    assert resultados[0].id == 1
    assert resultados[1].id == 2


def test_get_order_returns_none_if_not_found() -> None:
    mock_repo = MagicMock(spec=OrderRepository)
    mock_repo.get_order_by_id.return_value = None

    use_case = OrderUseCase(repository=mock_repo)
    resultado = use_case.get_order(9999)

    mock_repo.get_order_by_id.assert_called_once_with(9999)
    assert resultado is None


def test_create_new_order_fails_without_items() -> None:
    mock_repo = MagicMock(spec=OrderRepository)
    use_case = OrderUseCase(repository=mock_repo)

    items_data_vacios: List[Dict[str, Any]] = []

    with pytest.raises(ValueError, match="Una orden debe tener al menos un item"):
        use_case.create_new_order("test@example.com", items_data_vacios)

    mock_repo.create_order.assert_not_called()


def test_create_new_order_with_invalid_email() -> None:
    mock_repo = MagicMock(spec=OrderRepository)
    use_case = OrderUseCase(repository=mock_repo)

    items_data = [{"product_name": "Teclado", "price": 50.0, "quantity": 1}]

    with pytest.raises(ValueError, match="Email inválido"):
        use_case.create_new_order("test.com", items_data)

    mock_repo.create_order.assert_not_called()


def test_update_order_status_success_with_mock() -> None:
    mock_repo = MagicMock(spec=OrderRepository)
    item = OrderItem(product_name="Monitor", price=300.0, quantity=1)

    orden_actualizada = Order(
        id=7, customer_email="update@test.com", status="PAGADO", items=[item]
    )
    mock_repo.update_order_status.return_value = orden_actualizada

    use_case = OrderUseCase(repository=mock_repo)

    resultado = use_case.update_order_status(7, "PAGADO")

    mock_repo.update_order_status.assert_called_once_with(7, "PAGADO")
    assert resultado.status == "PAGADO"
    assert resultado.id == 7


def test_update_order_status_fails_if_invalid_status() -> None:
    mock_repo = MagicMock(spec=OrderRepository)
    use_case = OrderUseCase(repository=mock_repo)

    with pytest.raises(ValueError, match="Estado 'ESTADO_INVENTADO' no es válido"):
        use_case.update_order_status(7, "ESTADO_INVENTADO")

    mock_repo.update_order_status.assert_not_called()


def test_update_order_status_fails_if_not_found() -> None:
    mock_repo = MagicMock(spec=OrderRepository)
    mock_repo.update_order_status.return_value = None

    use_case = OrderUseCase(repository=mock_repo)

    with pytest.raises(
        ValueError, match="Orden con ID 99 no encontrada para actualizar"
    ):
        use_case.update_order_status(99, "ENVIADO")


def test_delete_order_success_with_mock() -> None:
    mock_repo = MagicMock(spec=OrderRepository)
    mock_repo.delete_order.return_value = True

    use_case = OrderUseCase(repository=mock_repo)

    use_case.delete_order(10)

    mock_repo.delete_order.assert_called_once_with(10)


def test_delete_order_fails_if_not_found() -> None:
    mock_repo = MagicMock(spec=OrderRepository)
    mock_repo.delete_order.return_value = False

    use_case = OrderUseCase(repository=mock_repo)

    with pytest.raises(
        ValueError, match="No se pudo eliminar, orden con ID 40 no encontrada"
    ):
        use_case.delete_order(40)
