import enum
import os

from fastapi_keycloak import FastAPIKeycloak

client_id = os.getenv("KEYCLOAK_CLIENT_ID")
client_secret = os.getenv("KEYCLOAK_CLIENT_SECRET")

idp = FastAPIKeycloak(
    server_url=os.getenv("KEYCLOAK_SERVER_URL"),
    client_id=client_id,
    client_secret=client_secret,
    admin_client_secret=os.getenv("KEYCLOAK_ADMIN_CLIENT_SECRET"),
    realm=os.getenv("KEYCLOAK_REALM"),
    callback_uri=os.getenv("KEYCLOAK_CALLBACK_URI"),
)


class UserRoles(str, enum.Enum):
    ADMIN_CHAT_HISTORY_VIEWER = "genie:admin:chat-history:viewer"
    ADMIN_USER_EXPERIENCE_VIEWER = "genie:admin:user-experience:viewer"
    ADMIN_USER_EXPERIENCE_EDITOR = "genie:admin:user-experience:editor"
    ADMIN_ANALYTICS_VIEWER = "genie:admin:analytics:viewer"
    AGENT_RESPONSE = "genie:agent:response"
    AGENT_END_CONVERSATION = "genie:agent:end_conversation"
