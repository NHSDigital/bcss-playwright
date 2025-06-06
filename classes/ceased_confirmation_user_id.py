from enum import Enum
from typing import Optional, Dict


class CeasedConfirmationUserId(Enum):
    AUTOMATED_PROCESS_ID = "automated process id"
    NULL = "null"
    NOT_NULL = "not null"
    USER_ID = "user's id"

    @classmethod
    def by_description(cls, description: str) -> Optional["CeasedConfirmationUserId"]:
        for item in cls:
            if item.value == description:
                return item
        return None

    def get_description(self) -> str:
        return self.value
