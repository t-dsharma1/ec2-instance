import enum

__all__ = ["Verbosity", "VerbosityType"]


class Verbosity(str, enum.Enum):
    """LLM verbosity levels for maximum amount of words allowed. Note that these limits
    are indicative and the LLM might loosely respect them.

    Attributes:
        SILENT: Maximum 30 words.
        MINIMAL: Maximum 50 words.
        NORMAL: Maximum 80 words.
        CHATTY: Maximum 130 words.
        TALKTIVE: Maximum 180 words.
        OVERSHARING: Maximum 250 words.
    """

    SILENT = "30"
    MINIMAL = "50"
    NORMAL = "80"
    CHATTY = "130"
    TALKTIVE = "180"
    OVERSHARING = "250"


class VerbosityType(str, enum.Enum):
    """LLM verbosity levels for maximum amount of words allowed. Note that these limits
    are indicative and the LLM might loosely respect them.

    Attributes:
        MINIMAL: Maximum 50 words.
        NORMAL: Maximum 80 words.
    """

    MINIMAL = "50"
    NORMAL = "80"
