import enum
from dataclasses import dataclass

from dataclasses_json import dataclass_json

__all__ = ["TranslatedData", "TranslationRequest", "TranslationLanguages", "DetectedTargetLanguage"]


@dataclass_json
@dataclass
class TranslationRequest:
    original_text: str
    target_language_code: str
    source_language_code: str | None = None


@dataclass_json
@dataclass
class TranslatedData:
    """Dataclass for the translated data."""

    translated_text: str
    source_language_code: str
    target_language_code: str


class TranslationLanguages(enum.Enum):
    """Enum for the translation languages."""

    ENGLISH = "en"
    AUTO = "auto"


class DetectedTargetLanguage(enum.Enum):
    """Enum for the detected target languages."""

    ENGLISH = "en"
    HINDI = "hi"
    OTHER = "other"
