from enum import Enum
from typing import Optional


class ManualCeaseRequested(Enum):
    NO = "no"
    DISCLAIMER_LETTER_REQUIRED = "yes - disclaimer letter required (c1)"
    DISCLAIMER_LETTER_SENT = "yes - disclaimer letter sent (c2)"
    YES = "yes"

    def __init__(self, description: str) -> None:
        self._description: str = description

    @property
    def description(self) -> str:
        return self._description

    @classmethod
    def by_description(cls, description: str) -> Optional["ManualCeaseRequested"]:
        for item in cls:
            if item.description == description:
                return item
        return None

    @classmethod
    def by_description_case_insensitive(
        cls, description: str
    ) -> Optional["ManualCeaseRequested"]:
        if description is None:
            return None
        for item in cls:
            if item.description.lower() == description.lower():
                return item
        return None
