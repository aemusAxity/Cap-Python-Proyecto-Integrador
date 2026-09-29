from datetime import datetime, timedelta, timezone
from typing import Any

import jwt
import pytest
from fastapi import HTTPException

from app.infrastructure.database import settings
from app.infrastructure.security import create_access_token, verify_token


def test_create_access_token() -> None:
    # Creamos un token real
    token = create_access_token({"sub": "user_test"})

    assert isinstance(token, str)

    payload = jwt.decode(
        token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
    )
    assert payload["sub"] == "user_test"
    assert "exp" in payload  # Debe tener fecha de expiración


def test_verify_token_success() -> None:
    # Creamos un token válido
    token = create_access_token({"sub": "usuario_valido"})

    username = verify_token(token)

    assert username == "usuario_valido"


def test_verify_token_fails_with_invalid_token() -> None:
    # Pasamos basura en lugar de un JWT
    with pytest.raises(HTTPException) as exc_info:
        verify_token("esto_no_es_un_token")

    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Credenciales inválidas"


def test_verify_token_fails_with_expired_token() -> None:
    # Fabricamos manualmente un token que expiró hace 10 minutos
    to_encode: dict[str, Any] = {"sub": "usuario_expirado"}
    expire = datetime.now(timezone.utc) - timedelta(minutes=10)
    to_encode.update({"exp": expire})

    token_expirado = jwt.encode(
        to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM
    )

    # El validador debe detectar que la fecha ya pasó
    with pytest.raises(HTTPException) as exc_info:
        verify_token(token_expirado)

    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Token expirado"


def test_verify_token_fails_without_subject() -> None:
    # Fabricamos un token válido matemáticamente, pero sin la llave "sub" (Username)
    to_encode = {"otro_dato": "valor"}
    token_incompleto = jwt.encode(
        to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM
    )

    # El validador exige que exista el 'sub'
    with pytest.raises(HTTPException) as exc_info:
        verify_token(token_incompleto)

    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Token inválido"
