from typing import Generator

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.infrastructure.database import Base

SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Fixture crea las tablas, entrega una sesión fresca, y luego borra todo
@pytest.fixture(scope="function")
def db_session() -> Generator[Session, None, None]:
    # Crear tablas
    Base.metadata.create_all(bind=engine)

    session = TestingSessionLocal()
    yield session

    session.close()
    Base.metadata.drop_all(bind=engine)
