from unittest.mock import AsyncMock, MagicMock

import httpx
import pytest
from fastapi import HTTPException

from genie_dao.services.superset.superset_db_service import (
    fetch_access_token,
    fetch_csrf_token,
    fetch_guest_token,
)

mock_fetch_access_token_response = {"access_token": "access_token", "refresh_token": "refresh_token"}


async def test_fetch_access_token():
    async with httpx.AsyncClient() as client:
        mock_response = MagicMock()
        mock_response.raise_for_status = MagicMock()
        mock_response.json.return_value = mock_fetch_access_token_response
        client.post = AsyncMock(return_value=mock_response)
        token = await fetch_access_token(client)
        client.post.assert_awaited_once()
        assert token == "access_token"


async def test_fetch_csrf_token_success():
    # Setup
    async with httpx.AsyncClient() as client:
        access_token = "valid_token"
        mock_response = MagicMock()
        mock_response.raise_for_status = MagicMock()
        mock_response.json.return_value = {"result": "csrf_token_value"}
        client.get = AsyncMock(return_value=mock_response)
        # Action
        csrf_token = await fetch_csrf_token(client, access_token)
        # Assert
        client.get.assert_awaited_once()
        assert csrf_token == "csrf_token_value"


async def test_fetch_csrf_token_failure():
    # Setup
    async with httpx.AsyncClient() as client:
        access_token = "valid_token"
        client.get = AsyncMock(
            side_effect=httpx.HTTPStatusError(message="Error", request=MagicMock(), response=MagicMock(status_code=401))
        )
        # Action & Assert
        with pytest.raises(HTTPException) as exc_info:
            await fetch_csrf_token(client, access_token)
        assert exc_info.value.status_code == 401
        assert "Error" in str(exc_info.value.detail)


async def test_fetch_guest_token_success():
    # Setup
    async with httpx.AsyncClient() as client:
        access_token = "valid_access_token"
        csrf_token = "valid_csrf_token"
        mock_response = MagicMock()
        mock_response.raise_for_status = MagicMock()
        mock_response.json.return_value = {"token": "guest_token_value"}
        client.post = AsyncMock(return_value=mock_response)

        # Action
        guest_token = await fetch_guest_token(client, access_token, csrf_token)

        # Assert
        client.post.assert_awaited_once()
        assert guest_token == "guest_token_value"


async def test_fetch_guest_token_failure():
    # Setup
    async with httpx.AsyncClient() as client:
        access_token = "valid_access_token"
        csrf_token = "valid_csrf_token"
        client.post = MagicMock(
            side_effect=httpx.HTTPStatusError(message="Error", request=MagicMock(), response=MagicMock(status_code=401))
        )

        # Action & Assert
        with pytest.raises(HTTPException) as exc_info:
            await fetch_guest_token(client, access_token, csrf_token)

        assert exc_info.value.status_code == 401
        assert "Error" in str(exc_info.value.detail)
