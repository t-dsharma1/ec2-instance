import enum


class ErrorRecovery(enum.Enum):
    RETRY = "RETRY"
    FALLBACK = "FALLBACK"
    GIVE_UP = "GIVE_UP"


class ErrorStrategy:
    """Error strategy for handling errors."""

    def __init__(self, fallback_retries: int = 3, max_retries: int = 5):
        assert fallback_retries < max_retries, "fallback_retries must be less than max_retries"
        self.fallback_retries = fallback_retries
        self.max_retries = max_retries

    def decide(self, retry_count: int) -> ErrorRecovery:
        """Decides the next action based on the error type and retry count."""
        if retry_count < self.fallback_retries:
            return ErrorRecovery.RETRY
        elif retry_count < self.max_retries:
            return ErrorRecovery.FALLBACK
        else:
            return ErrorRecovery.GIVE_UP
