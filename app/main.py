from typing import Generator, List

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.application.use_cases import OrderUseCase
from app.domain.models import Order
from app.infrastructure.database import SessionLocal
from app.infrastructure.repositories import SQLAlchemyOrderRepository
from app.infrastructure.security import create_access_token, verify_token
from app.schemas import OrderCreate, OrderResponse, OrderStatusUpdate

app = FastAPI(title="Orders API - Proyecto Integrador", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_order_use_case(db: Session = Depends(get_db)) -> OrderUseCase:
    repository = SQLAlchemyOrderRepository(session=db)
    return OrderUseCase(repository=repository)


# --- ENDPOINTS ---


@app.post("/token")
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()) -> dict:
    """Endpoint para iniciar sesión. Recibe username y password, devuelve el JWT."""
    if form_data.password != "secreto":
        raise HTTPException(status_code=401, detail="Contraseña incorrecta")

    access_token = create_access_token(data={"sub": form_data.username})
    return {"access_token": access_token, "token_type": "bearer"}


@app.post(
    "/orders/",
    response_model=OrderResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(verify_token)],
)
def create_order(
    order_in: OrderCreate, use_case: OrderUseCase = Depends(get_order_use_case)
) -> Order:
    try:
        items_data = [item.model_dump() for item in order_in.items]
        order = use_case.create_new_order(order_in.customer_email, items_data)
        return order
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@app.get(
    "/orders/", response_model=List[OrderResponse], dependencies=[Depends(verify_token)]
)
def list_orders(use_case: OrderUseCase = Depends(get_order_use_case)) -> List[Order]:
    orders = use_case.list_orders()
    return orders


@app.get(
    "/orders/{order_id}",
    response_model=OrderResponse,
    dependencies=[Depends(verify_token)],
)
def get_order(
    order_id: int, use_case: OrderUseCase = Depends(get_order_use_case)
) -> Order:
    order = use_case.get_order(order_id)

    if order is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Orden no encontrada"
        )

    return order


@app.patch(
    "/orders/{order_id}/status",
    response_model=OrderResponse,
    dependencies=[Depends(verify_token)],
)
def update_order_status(
    order_id: int,
    update_data: OrderStatusUpdate,
    use_case: OrderUseCase = Depends(get_order_use_case),
) -> Order:
    try:
        updated_order = use_case.update_order_status(order_id, update_data.status)
        return updated_order
    except ValueError as e:
        if "no encontrada" in str(e):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@app.delete(
    "/orders/{order_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(verify_token)],
)
def delete_order(
    order_id: int, use_case: OrderUseCase = Depends(get_order_use_case)
) -> None:
    try:
        use_case.delete_order(order_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
