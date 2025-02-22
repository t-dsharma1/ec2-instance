import os
from typing import Optional

import httpx
from fastapi import HTTPException

SUPERSET_BASE_URL = os.getenv("SUPERSET_BASE_URL")
SUPERSET_DASHBOARD_ID = os.getenv("SUPERSET_DASHBOARD_ID")
SUPERSET_USERNAME = os.getenv("SUPERSET_USERNAME")
SUPERSET_PASSWORD = os.getenv("SUPERSET_PASSWORD")
SUPERSET_FIRSTNAME = os.getenv("SUPERSET_FIRSTNAME")
SUPERSET_LASTNAME = os.getenv("SUPERSET_LASTNAME")

SUPERSET_PATH = "api/v1/security"


@staticmethod
async def fetch_access_token(client: httpx.AsyncClient) -> Optional[str]:
    """Fetch access token from Superset API.

    Parameters:
    - client (httpx.AsyncClient): The HTTP client.

    Returns:
    - str: The access token.

    Raises:
    - HTTPException: If there's an error fetching the access token.
    """
    try:
        response = await client.post(
            f"{SUPERSET_PATH}/login",
            json={
                "username": SUPERSET_USERNAME,
                "password": SUPERSET_PASSWORD,
                "provider": "db",
                "refresh": True,
            },
        )
        response.raise_for_status()
        return response.json().get("access_token")
    except httpx.HTTPError as e:
        raise HTTPException(status_code=e.response.status_code, detail=str(e))


@staticmethod
async def fetch_csrf_token(client: httpx.AsyncClient, access_token: str) -> Optional[str]:
    """Fetch CSRF token from Superset API.

    Parameters:
    - client (httpx.AsyncClient): The HTTP client.
    - access_token (str): The access token.

    Returns:
    - str: The CSRF token.

    Raises:
    - HTTPException: If there's an error fetching the CSRF token.
    """
    headers = {"Authorization": f"Bearer {access_token}"}
    try:
        response = await client.get(f"{SUPERSET_PATH}/csrf_token/", headers=headers)
        response.raise_for_status()
        return response.json().get("result")
    except httpx.HTTPError as e:
        raise HTTPException(status_code=e.response.status_code, detail=str(e))


@staticmethod
async def fetch_guest_token(client: httpx.AsyncClient, access_token: str, csrf_token: str) -> Optional[str]:
    """Fetch guest token from Superset API.

    Parameters:
    - client (httpx.AsyncClient): The HTTP client.
    - access_token (str): The access token.
    - csrf_token (str): The CSRF token.

    Returns:
    - str: The guest token.

    Raises:
    - HTTPException: If there's an error fetching the guest token.
    """
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Referer": f"{SUPERSET_BASE_URL}/{SUPERSET_PATH}/csrf_token/",
        "X-CSRFToken": csrf_token,
    }
    body = {
        "resources": [
            {"type": "dashboard", "id": SUPERSET_DASHBOARD_ID},
        ],
        "rls": [],
        "user": {"username": SUPERSET_USERNAME, "first_name": SUPERSET_FIRSTNAME, "last_name": SUPERSET_LASTNAME},
    }
    try:
        response = await client.post(f"{SUPERSET_PATH}/guest_token/", json=body, headers=headers)
        response.raise_for_status()
        return response.json().get("token")
    except httpx.HTTPError as e:
        raise HTTPException(status_code=e.response.status_code, detail=str(e))
