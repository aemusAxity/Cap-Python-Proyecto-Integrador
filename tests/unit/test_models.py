import pytest

from app.domain.models import Order, OrderItem


def test_order_item_subtotal() -> None:
    item = OrderItem(product_name="Laptop", price=1000.0, quantity=2)
    assert item.subtotal == 2000.0


def test_order_total_amount() -> None:
    items = [OrderItem("Mouse", 50.0, 2), OrderItem("Teclado", 100.0, 1)]
    order = Order(customer_email="test@example.com", items=items)

    assert order.total_amount == 200.0


def test_order_creation_fails_without_items() -> None:
    with pytest.raises(ValueError, match="Una orden debe tener al menos un item"):
        Order(customer_email="test@example.com", items=[])


def test_order_creation_fails_with_invalid_email() -> None:
    item = OrderItem("Cable", 10.0, 1)
    with pytest.raises(ValueError, match="Email inválido"):
        Order(customer_email="correo_invalido", items=[item])
