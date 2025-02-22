import datetime

from pydantic import BaseModel, Field, field_validator

# API Request Definition for standard WhatsApp message event hook
#
# Example Request:
#
# {
#   'object': 'whatsapp_business_account',
#   'entry': [
#     {
#       'id': '237466612793286',
#       'changes': [
#         {
#           'value': {
#             'messaging_product': 'whatsapp',
#             'metadata': {
#               'display_phone_number': '65123456789',
#               'phone_number_id': '291324484063305'
#             },
#             'contacts': [
#               {
#                 'profile': {
#                   'name': 'Joe'
#                 },
#                 'wa_id': '49123456789'
#               }
#             ],
#             'messages': [
#               {
#                 'from': '49123456789',
#                 'id': 'wamid.HBgNNDkxNTE2ODk1MTM5MxUCABIYFDNBNTlFOEI3QjVDQTAxOTUxRkRBAA==',
#                 'timestamp': '1714412098',
#                 'text': {
#                   'body': 'Hello'
#                 },
#                 'type': 'text'
#               }
#             ]
#           },
#           'field': 'messages'
#         }
#       ]
#     }
#   ]
# }


class WhatsAppHookRequestEntryChangesValueContactProfile(BaseModel):
    name: str


class WhatsAppHookRequestEntryChangesValueContact(BaseModel):
    profile: WhatsAppHookRequestEntryChangesValueContactProfile
    wa_id: str


class WhatsAppHookRequestEntryChangesValueMetadata(BaseModel):
    display_phone_number: str
    phone_number_id: str


class WhatsAppHookRequestEntryChangesValueMessageText(BaseModel):
    body: str


class WhatsAppHookRequestEntryChangesValueMessage(BaseModel):
    from_: str = Field(alias="from")
    id: str
    text: WhatsAppHookRequestEntryChangesValueMessageText
    timestamp: datetime.datetime | int
    type: str

    @field_validator("timestamp", mode="after")
    @classmethod
    def convert_timestamp(cls, v: datetime.datetime | int) -> datetime.datetime:
        if isinstance(v, datetime.datetime):
            return v
        elif isinstance(v, int):
            return datetime.datetime.fromtimestamp(v / 1000.0)
        else:
            raise TypeError(f"timestamp is neither datetime nor int: {v}")


class WhatsAppHookRequestEntryChangesValue(BaseModel):
    messaging_product: str
    metadata: WhatsAppHookRequestEntryChangesValueMetadata
    messages: list[WhatsAppHookRequestEntryChangesValueMessage]
    contacts: list[WhatsAppHookRequestEntryChangesValueContact]


class WhatsAppHookRequestEntryChanges(BaseModel):
    value: WhatsAppHookRequestEntryChangesValue
    field: str


class WhatsAppHookRequestEntry(BaseModel):
    id: str
    changes: list[WhatsAppHookRequestEntryChanges]


class WhatsAppHookRequest(BaseModel):
    object: str
    entry: list[WhatsAppHookRequestEntry]
