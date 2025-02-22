import os

import httpx
from fastapi import APIRouter, Depends
from fastapi_keycloak import OIDCUser

from connectai.handlers import get_or_create_logger
from connectai.handlers.utils.api_idp import UserRoles, idp
from genie_dao.services import fetch_access_token, fetch_csrf_token, fetch_guest_token

logger = get_or_create_logger(logger_name="supersetLoginAPI")

router = APIRouter()

SUPERSET_BASE_URL = os.getenv("SUPERSET_BASE_URL")


@router.get("/guest-token")
async def fetch_guest_token_api(
    _current_user: OIDCUser = Depends(idp.get_current_user(required_roles=[UserRoles.ADMIN_ANALYTICS_VIEWER])),
):
    """Fetch guest token from Superset API to access the dashboard.

    Parameters:
    - current_user (str): The current user.

    Returns:
    - str: The guest token.
    """
    async with httpx.AsyncClient(base_url=SUPERSET_BASE_URL, headers={"Content-Type": "application/json"}) as client:
        access_token = await fetch_access_token(client)
        csrf_token = await fetch_csrf_token(client, access_token)
        guest_token = await fetch_guest_token(client, access_token, csrf_token)
        return guest_token
