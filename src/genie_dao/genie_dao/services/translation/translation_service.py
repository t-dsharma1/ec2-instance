from genie_core.utils import logging
from genie_dao.datamodel import TranslatedData, TranslationRequest
from genie_dao.utils.aws_service import AWSTranslationHandler

_log = logging.get_or_create_logger()


class TranslationService:
    def __init__(self):
        self.aws_handler = AWSTranslationHandler()

    async def translate(self, request: TranslationRequest):
        # Add any pre-processing or validation logic here
        if request.source_language_code is None:
            request.source_language_code = "auto"
        return await self.aws_handler.translate_text(
            request.original_text, request.source_language_code, request.target_language_code
        )


async def auto_translate(request: TranslationRequest) -> dict:
    translator = TranslationService()
    response = await translator.translate(request)
    return response


async def translate(text: str, source_language_code: str = "auto", target_language_code: str = "en") -> TranslatedData:
    _log.info(f"Translating text: {text} from {source_language_code} to {target_language_code}")
    response = await auto_translate(
        TranslationRequest(
            original_text=text, source_language_code=source_language_code, target_language_code=target_language_code
        )
    )

    # Extracting the response data
    response_data = response
    response_source_language_code = response_data.get("SourceLanguageCode", "Unknown")
    response_target_source_language_code = response_data.get("TargetLanguageCode", "Unknown")
    response_translated_text = response_data.get("TranslatedText", "Translation not available")

    item = {
        "translated_text": response_translated_text,
        "source_language_code": response_source_language_code,
        "target_language_code": response_target_source_language_code,
    }
    return TranslatedData(**item)
