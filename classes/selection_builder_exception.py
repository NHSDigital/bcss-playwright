from typing import Optional


class SelectionBuilderException(Exception):
    """
    This exception is used for subject selection when an error occurs.
    """

    def __init__(self, message_or_key: str, value: Optional[str] = None):
        if value is None:
            message = message_or_key
        else:
            message = f"Invalid '{message_or_key}' value: '{value}'"
        super().__init__(message)
