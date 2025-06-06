from enum import Enum
from typing import Optional


class CeasedConfirmationDetails(Enum):
    NULL = "null"
    NOT_NULL = "not null"

    @classmethod
    def by_description(cls, description: str) -> Optional["CeasedConfirmationDetails"]:
        for item in cls:
            if item.value == description:
                return item
        return None

    def get_description(self) -> str:
        return self.value
