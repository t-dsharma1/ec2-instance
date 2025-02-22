import requests

from genie_core.utils import logging

_log = logging.get_or_create_logger()


def message_whatsapp(to_number: str, text: str, waba_url: str, waba_token: str):
    url = waba_url

    headers = {
        "Authorization": f"Bearer {waba_token}",
        "Content-Type": "application/json",
    }

    data = {"messaging_product": "whatsapp", "to": to_number, "text": {"body": text}}

    response = requests.post(url, headers=headers, json=data)

    if response.status_code == 200:
        _log.info("Message sent successfully.")
    else:
        _log.error(f"Failed to send message. Status code: {response.status_code}, Response: {response.text}")
