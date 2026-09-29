from datetime import datetime, timezone

from app.schemas import ItemCreate, OrderCreate, OrderResponse, OrderStatusUpdate


def test_order_response_date_serializer() -> None:
    fecha_fija = datetime(2026, 9, 29, 1, 25, 34, tzinfo=timezone.utc)

    # 2. Act: Instanciamos el esquema de salida con esa fecha
    esquema = OrderResponse(
        id=1,
        customer_email="test@example.com",
        status="PENDIENTE",
        total_amount=500.0,
        created_at=fecha_fija,
        items=[],
    )

    datos_json = esquema.model_dump()

    assert datos_json["created_at"] == "29/09/2026 01:25:34"


def test_order_status_update_schema() -> None:
    esquema = OrderStatusUpdate(status="PAGADO")
    assert esquema.status == "PAGADO"


def test_order_create_schema() -> None:
    item = ItemCreate(product_name="Cable", price=10.0, quantity=2)
    esquema = OrderCreate(customer_email="test@example.com", items=[item])

    assert esquema.customer_email == "test@example.com"
    assert len(esquema.items) == 1
    assert esquema.items[0].product_name == "Cable"
