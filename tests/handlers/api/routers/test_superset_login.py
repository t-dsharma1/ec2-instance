from unittest.mock import AsyncMock, MagicMock, patch

from fastapi_keycloak import FastAPIKeycloak

# Patch the `FastAPIKeycloak` methods before importing the module
with patch.object(FastAPIKeycloak, "__init__", return_value=None), patch(
    "connectai.handlers.utils.api_idp.FastAPIKeycloak._get_admin_token", return_value=None
), patch("connectai.handlers.utils.api_idp.FastAPIKeycloak.open_id_configuration", new_callable=MagicMock), patch(
    "connectai.handlers.utils.api_idp.FastAPIKeycloak.token_uri", new_callable=MagicMock
), patch(
    "connectai.handlers.utils.api_idp.FastAPIKeycloak", new_callable=MagicMock
), patch(
    "connectai.handlers.utils.api_idp", new_callable=MagicMock
), patch(
    "connectai.handlers.utils.api_idp.idp.get_current_user", new_callable=MagicMock
), patch(
    "connectai.handlers.utils.api_idp.FastAPIKeycloak.public_key", new_callable=MagicMock
):
    from connectai.handlers.api.routers.superset_login import fetch_guest_token_api


@patch("connectai.handlers.api.routers.superset_login.fetch_guest_token", return_value=AsyncMock)
@patch("connectai.handlers.api.routers.superset_login.fetch_csrf_token", return_value=AsyncMock)
@patch("connectai.handlers.api.routers.superset_login.fetch_access_token", return_value=AsyncMock)
async def test_fetch_guest_token_api(mock_fetch_access_token, mock_fetch_csrf_token, mock_fetch_guest_token):
    mock_fetch_access_token.return_value = None
    mock_fetch_csrf_token.return_value = None
    mock_fetch_guest_token.return_value = None
    await fetch_guest_token_api()
    mock_fetch_access_token.assert_awaited_once()
    mock_fetch_csrf_token.assert_awaited_once()
    mock_fetch_guest_token.assert_awaited_once()
