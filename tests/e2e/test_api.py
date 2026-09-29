from typing import Dict, Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.infrastructure.database import Base
from app.main import app, get_db

SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db() -> Generator:
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


# FastAPI usara la BD temporal
app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_database() -> Generator:
    """Crea las tablas antes de cada test y las borra al terminar."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def auth_headers() -> Dict[str, str]:
    """Hace login automáticamente y devuelve los headers con el JWT."""
    respuesta = client.post("/token", data={"username": "aerin", "password": "secreto"})
    token = respuesta.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_login_success() -> None:
    respuesta = client.post("/token", data={"username": "aerin", "password": "secreto"})

    assert respuesta.status_code == 200
    assert "access_token" in respuesta.json()
    assert respuesta.json()["token_type"] == "bearer"


def test_login_fails_with_wrong_password() -> None:
    respuesta = client.post("/token", data={"username": "aerin", "password": "hacker"})
    assert respuesta.status_code == 401
    assert respuesta.json()["detail"] == "Contraseña incorrecta"


def test_create_order_without_token_is_rejected() -> None:
    datos_entrada = {
        "customer_email": "test@test.com",
        "items": [{"product_name": "Laptop", "price": 1000.0, "quantity": 1}],
    }
    respuesta = client.post("/orders/", json=datos_entrada)
    # Debe bloquearlo el cadenero de FastAPI
    assert respuesta.status_code == 401


def test_create_order_success(auth_headers: Dict[str, str]) -> None:
    datos_entrada = {
        "customer_email": "real@test.com",
        "items": [{"product_name": "Monitor", "price": 300.0, "quantity": 2}],
    }

    respuesta = client.post("/orders/", json=datos_entrada, headers=auth_headers)

    assert respuesta.status_code == 201
    datos = respuesta.json()
    assert datos["customer_email"] == "real@test.com"
    assert datos["total_amount"] == 600.0
    assert datos["status"] == "PENDIENTE"
    assert "created_at" in datos
    assert datos["id"] is not None


def test_list_all_orders(auth_headers: Dict[str, str]) -> None:
    # 1. Crear una orden primero
    datos_entrada = {
        "customer_email": "test@example.com",
        "items": [{"product_name": "Mouse", "price": 50.0, "quantity": 1}],
    }
    client.post("/orders/", json=datos_entrada, headers=auth_headers)

    # 2. Consultar lista
    respuesta = client.get("/orders/", headers=auth_headers)

    assert respuesta.status_code == 200
    datos = respuesta.json()
    assert len(datos) == 1
    assert datos[0]["customer_email"] == "test@example.com"


def test_get_order_by_id_success(auth_headers: Dict[str, str]) -> None:
    # Crear
    datos_entrada = {
        "customer_email": "findme@test.com",
        "items": [{"product_name": "Cable", "price": 10.0, "quantity": 1}],
    }
    respuesta_creacion = client.post(
        "/orders/", json=datos_entrada, headers=auth_headers
    )
    id_orden = respuesta_creacion.json()["id"]

    # Consultar por ID
    respuesta = client.get(f"/orders/{id_orden}", headers=auth_headers)

    assert respuesta.status_code == 200
    assert respuesta.json()["customer_email"] == "findme@test.com"


def test_get_order_by_id_fails_not_found(auth_headers: Dict[str, str]) -> None:
    respuesta = client.get("/orders/9999", headers=auth_headers)
    assert respuesta.status_code == 404
    assert "no encontrada" in respuesta.json()["detail"]


def test_update_order_status_success(auth_headers: Dict[str, str]) -> None:
    # Crear
    datos_entrada = {
        "customer_email": "update@test.com",
        "items": [{"product_name": "Desk", "price": 100.0, "quantity": 1}],
    }
    respuesta_creacion = client.post(
        "/orders/", json=datos_entrada, headers=auth_headers
    )
    id_orden = respuesta_creacion.json()["id"]

    # Actualizar
    datos_actualizacion = {"status": "PAGADO"}
    respuesta = client.patch(
        f"/orders/{id_orden}/status", json=datos_actualizacion, headers=auth_headers
    )

    assert respuesta.status_code == 200
    assert respuesta.json()["status"] == "PAGADO"


def test_update_order_status_fails_not_found(auth_headers: Dict[str, str]) -> None:
    datos_actualizacion = {"status": "PAGADO"}
    respuesta = client.patch(
        "/orders/9999/status", json=datos_actualizacion, headers=auth_headers
    )

    assert respuesta.status_code == 404
    assert "no encontrada para actualizar" in respuesta.json()["detail"]


def test_update_order_status_fails_invalid_status(auth_headers: Dict[str, str]) -> None:
    # Crear
    datos_entrada = {
        "customer_email": "badstatus@test.com",
        "items": [{"product_name": "A", "price": 1.0, "quantity": 1}],
    }
    respuesta_creacion = client.post(
        "/orders/", json=datos_entrada, headers=auth_headers
    )
    id_orden = respuesta_creacion.json()["id"]

    # Actualizar con estado erróneo
    datos_actualizacion = {"status": "ESTADO_HACKEADO"}
    respuesta = client.patch(
        f"/orders/{id_orden}/status", json=datos_actualizacion, headers=auth_headers
    )

    assert respuesta.status_code == 400
    assert "no es válido" in respuesta.json()["detail"]


def test_delete_order_success(auth_headers: Dict[str, str]) -> None:
    # Crear
    datos_entrada = {
        "customer_email": "delete@test.com",
        "items": [{"product_name": "B", "price": 1.0, "quantity": 1}],
    }
    respuesta_creacion = client.post(
        "/orders/", json=datos_entrada, headers=auth_headers
    )
    id_orden = respuesta_creacion.json()["id"]

    # Eliminar
    respuesta_borrado = client.delete(f"/orders/{id_orden}", headers=auth_headers)

    assert respuesta_borrado.status_code == 204

    # Verificar que ya no existe
    respuesta_consulta = client.get(f"/orders/{id_orden}", headers=auth_headers)
    assert respuesta_consulta.status_code == 404


def test_delete_order_fails_not_found(auth_headers: Dict[str, str]) -> None:
    respuesta = client.delete("/orders/9999", headers=auth_headers)

    assert respuesta.status_code == 404
    assert "no encontrada" in respuesta.json()["detail"]
