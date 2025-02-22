import enum

__all__ = ["Language"]


class Language(str, enum.Enum):
    """Supported languages for the translation layer.

    Language codes as of ISO 639-1
    """

    EN = "English"
    HI = "Hindi"
    ES = "Spanish"
