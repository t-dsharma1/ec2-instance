from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import HTTPException
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
    from connectai.handlers.api.routers.flow_builder import (
        create_flow,
        delete_flow,
        get_flow_details,
        get_flow_list,
        get_template_list,
    )
    from genie_dao.datamodel.chatbot_db_model.models import (
        Flow,
        FlowCallSightConfig,
        FlowStateMachine,
        FlowStateMachineConfig,
        FlowStateMachineFlowSupervisor,
        FlowStateMachineState,
        VariantConfig,
    )

mocked_flow_state_machine = FlowStateMachine(
    FlowConfig=FlowStateMachineConfig(
        is_ai_first_message=True,
        translation_service_enabled=True,
        variants_config=VariantConfig(variants_weights=[1, 2]),
        flow_supervisor=FlowStateMachineFlowSupervisor(),
        callsight=FlowCallSightConfig(enabled=False),
    ),
    FlowStates={"mock_flow_states": FlowStateMachineState(next_states=["mock_states"])},
)

mock_flow_response = {
    "PK": "CONVERSATION#97869P21HG7OTRFW",
    "SK": "METADATA#2024-05-20T10:00:00",
    "flow_states": {},
    "flow_state_machine": mocked_flow_state_machine,
    "flow_context_map": {},
    "flow_base_config": "flow_base_config",
    "flow_config_llm_prompts": {},
    "flow_utility_prompts": {},
    "flow_display_name": "",
    "flow_description": "",
    "item_type": "item_type",
    "item_created_datetime": "2024-05-20T12:00:00",
    "item_deleted_datetime": None,
    "channel": None,
    "product_segment": None,
    "experience_type": None,
}


@patch("connectai.handlers.api.routers.flow_builder.get_latest_flow_metadata_list", new_callable=AsyncMock)
async def test_get_flow_list(mock_get_latest_flow_metadata_list):
    mock_get_latest_flow_metadata_list.return_value = None
    await get_flow_list(current_user="mock_user")
    mock_get_latest_flow_metadata_list.assert_awaited_once()


@patch("connectai.handlers.api.routers.flow_builder.get_latest_flow_template_list", new_callable=AsyncMock)
async def test_get_template_list(mock_get_latest_flow_template_list):
    mock_get_latest_flow_template_list.return_value = None
    await get_template_list()
    mock_get_latest_flow_template_list.assert_awaited_once()


@patch("connectai.handlers.api.routers.flow_builder.get_latest_flow_variants_metadata", new_callable=AsyncMock)
async def test_get_flow_details_if_none(mock_get_latest_flow_variants_metadata):
    mock_get_latest_flow_variants_metadata.return_value = None
    with pytest.raises(HTTPException):
        await get_flow_details(flow_id="mock_flow_id")


@patch("connectai.handlers.api.routers.flow_builder.get_latest_flow_variants_metadata", new_callable=AsyncMock)
async def test_get_flow_details_if_not_none(mock_get_latest_flow_variants_metadata):
    mock_get_latest_flow_variants_metadata.return_value = ""
    await get_flow_details(flow_id="mock_flow_id")
    mock_get_latest_flow_variants_metadata.assert_awaited_once()


@patch("connectai.handlers.api.routers.flow_builder.create_flow_metadata", new_callable=AsyncMock)
async def test_create_flow(mock_create_flow_metadata):
    mock_create_flow_metadata.return_value = None
    await create_flow(request=Flow(**mock_flow_response))
    mock_create_flow_metadata.assert_awaited_once()


@patch("connectai.handlers.api.routers.flow_builder.soft_delete_flow", new_callable=AsyncMock)
async def test_delete_flow_if_none(mock_soft_delete_flow):
    mock_soft_delete_flow.return_value = None
    with pytest.raises(HTTPException):
        await delete_flow(flow_id="mock_flow_id")


@patch("connectai.handlers.api.routers.flow_builder.soft_delete_flow", new_callable=AsyncMock)
async def test_delete_flow_if_not_none(mock_soft_delete_flow):
    mock_soft_delete_flow.return_value = ""
    response = await delete_flow(flow_id="mock_flow_id")
    assert response == {"status": "success"}
