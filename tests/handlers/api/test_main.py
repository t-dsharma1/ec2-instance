from unittest.mock import MagicMock, patch

from fastapi import status
from fastapi.testclient import TestClient
from fastapi_keycloak import FastAPIKeycloak

from connectai.handlers.queue.sqs import SQSQueuePublisher

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
), patch(
    "connectai.handlers.utils.api_idp.idp.add_swagger_config", new_callable=MagicMock
), patch(
    "threading.Thread"
), patch.object(
    SQSQueuePublisher, "__init__", return_value=None
), patch(
    "connectai.handlers.queue.sqs.SQSMessageHandler", new_callable=MagicMock
), patch(
    "connectai.handlers.queue.sqs.SQSMessageHandler", new_callable=MagicMock
), patch(
    "connectai.handlers.queue.sqs.SQSMessageHandler", new_callable=MagicMock
), patch(
    "connectai.handlers.queue.sqs.SQSQueue", new_callable=MagicMock
):
    from connectai.handlers.api.main import app

client = TestClient(app)


def test_app_routes():
    response = client.get("/metrics")
    assert response.status_code == status.HTTP_400_BAD_REQUEST
