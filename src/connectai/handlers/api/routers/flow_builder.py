from fastapi import APIRouter, Depends, HTTPException
from fastapi_keycloak import OIDCUser

from connectai.handlers.utils.api_idp import UserRoles, idp
from genie_core.utils import logging
from genie_dao.datamodel.chatbot_db_model import models
from genie_dao.services import (
    create_flow_metadata,
    get_latest_flow_metadata_list,
    get_latest_flow_template_list,
    get_latest_flow_variants_metadata,
    soft_delete_flow,
)

_log = logging.get_or_create_logger()

router = APIRouter()


@router.get("/flow", response_model=list[list[models.Flow]])
async def get_flow_list(
    current_user: OIDCUser = Depends(idp.get_current_user(required_roles=[UserRoles.ADMIN_USER_EXPERIENCE_VIEWER])),
) -> list[list[models.Flow]]:
    """Get the list of flows.

    Parameters:
    - current_user (str): The current user.

    Returns:
    - list[StateMachineItem]: The list of flows.
    """
    _log.info(f"user is {current_user}")
    return await get_latest_flow_metadata_list()


@router.get("/flow-template", response_model=list[list[models.Flow]])
async def get_template_list(
    current_user: OIDCUser = Depends(idp.get_current_user(required_roles=[UserRoles.ADMIN_USER_EXPERIENCE_VIEWER])),
):
    _log.info(f"user is {current_user}")
    return await get_latest_flow_template_list()


@router.get("/flow/{flow_id}", response_model=list[models.Flow])
async def get_flow_details(
    flow_id,
    current_user: OIDCUser = Depends(idp.get_current_user(required_roles=[UserRoles.ADMIN_USER_EXPERIENCE_VIEWER])),
) -> list[models.Flow]:
    """Get the ordered flow variants metadata for the given flow ID.

    Parameters:
    - flow_id (str): The flow ID.
    - current_user (str): The current user.

    Returns:
    - StateMachineItem: The flow metadata.
    """
    _log.info(f"user is {current_user}")
    data = await get_latest_flow_variants_metadata(flow_id)
    if data is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return data


@router.post("/flow")
async def create_flow(
    request: models.Flow,
    current_user: OIDCUser = Depends(idp.get_current_user(required_roles=[UserRoles.ADMIN_USER_EXPERIENCE_EDITOR])),
) -> dict:
    """Create the flow variant metadata.

    Parameters:
    - request (APICreateFlowRequestPayload): The request payload.
    - current_user (str): The current user.

    Returns:
    - dict: The dict containing message with success status.
    """
    _log.info(f"user is {current_user}")
    return await create_flow_metadata(flow_item=request)


@router.delete("/flow/{flow_id}")
async def delete_flow(
    flow_id: str,
    current_user: OIDCUser = Depends(idp.get_current_user(required_roles=[UserRoles.ADMIN_USER_EXPERIENCE_EDITOR])),
) -> dict:
    """Soft delete all flow variants and history items.

    Parameters:
    - flow_id (str): The ID of the flow to delete
    - current_user (str): The current user.

    Returns:
    - dict: The dict containing message with success status.
    """
    _log.info(f"user is {current_user}")
    deleted_items = await soft_delete_flow(flow_id=flow_id)
    if deleted_items is None:
        raise HTTPException(status_code=404, detail="Item not found")

    return {"status": "success"}
