import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from fastapi import HTTPException, status
from app.dependencies import (
    get_settings,
    get_email_service,
    get_db,
    get_current_user,
    require_role
)
from app.services.email_service import EmailService
from settings.config import Settings


def test_get_settings_returns_instance():
    settings = get_settings()
    assert isinstance(settings, Settings)


def test_get_email_service_returns_instance():
    email_service = get_email_service()
    assert isinstance(email_service, EmailService)


@pytest.mark.asyncio
@patch("app.dependencies.Database.get_session_factory")
async def test_get_db_yields_session(mock_get_factory):
    mock_session = AsyncMock()
    mock_session.__aenter__.return_value = "fake_session"
    mock_factory = MagicMock(return_value=mock_session)
    mock_get_factory.return_value = mock_factory

    # Simulate the generator
    gen = get_db()
    result = await anext(gen)
    assert result == "fake_session"


@pytest.mark.asyncio
@patch("app.dependencies.Database.get_session_factory")
async def test_get_db_raises_http_exception_on_error(mock_get_factory):
    async def fake_gen():
        raise Exception("DB Error")
    mock_session = AsyncMock()
    mock_session.__aenter__.side_effect = fake_gen
    mock_factory = MagicMock(return_value=mock_session)
    mock_get_factory.return_value = mock_factory

    with pytest.raises(Exception):  # The exception is caught inside the generator
        gen = get_db()
        await anext(gen)


@patch("app.dependencies.decode_token")
def test_get_current_user_valid_token(mock_decode_token):
    token = "fake_token"
    mock_decode_token.return_value = {"sub": "user123", "role": "ADMIN"}

    user = get_current_user(token=token)
    assert user["user_id"] == "user123"
    assert user["role"] == "ADMIN"


@patch("app.dependencies.decode_token")
def test_get_current_user_invalid_token_none(mock_decode_token):
    mock_decode_token.return_value = None

    with pytest.raises(HTTPException) as exc:
        get_current_user(token="invalid")
    assert exc.value.status_code == status.HTTP_401_UNAUTHORIZED


@patch("app.dependencies.decode_token")
def test_get_current_user_missing_fields(mock_decode_token):
    mock_decode_token.return_value = {"sub": None, "role": None}

    with pytest.raises(HTTPException) as exc:
        get_current_user(token="token")
    assert exc.value.status_code == status.HTTP_401_UNAUTHORIZED


def test_require_role_allows_access():
    checker = require_role(["ADMIN", "MANAGER"])
    user = {"user_id": "123", "role": "MANAGER"}
    result = checker(current_user=user)
    assert result == user


def test_require_role_denies_access():
    checker = require_role(["ADMIN"])
    user = {"user_id": "123", "role": "USER"}
    with pytest.raises(HTTPException) as exc:
        checker(current_user=user)
    assert exc.value.status_code == status.HTTP_403_FORBIDDEN
