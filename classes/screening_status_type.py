from enum import Enum
from typing import Optional


class ScreeningStatusType(Enum):
    CALL = (4001, "Call")
    INACTIVE = (4002, "Inactive")
    OPT_IN = (4003, "Opt-in")
    RECALL = (4004, "Recall")
    SELF_REFERRAL = (4005, "Self-referral")
    SURVEILLANCE = (4006, "Surveillance")
    SEEKING_FURTHER_DATA = (4007, "Seeking Further Data")
    CEASED = (4008, "Ceased")
    BOWEL_SCOPE = (4009, "Bowel Scope")
    LYNCH = (306442, "Lynch Surveillance")
    LYNCH_SELF_REFERRAL = (307129, "Lynch Self-referral")
    NULL = (0, "Null")
    NOT_NULL = (0, "Not null")

    def __init__(self, valid_value_id: int, description: str):
        self._value_id = valid_value_id
        self._description = description

    @property
    def valid_value_id(self) -> int:
        return self._value_id

    @property
    def description(self) -> str:
        return self._description

    @classmethod
    def by_description(cls, description: str) -> Optional["ScreeningStatusType"]:
        for item in cls:
            if item.description == description:
                return item
        return None

    @classmethod
    def by_description_case_insensitive(
        cls, description: str
    ) -> Optional["ScreeningStatusType"]:
        description = description.lower()
        for item in cls:
            if item.description.lower() == description:
                return item
        return None

    @classmethod
    def by_valid_value_id(cls, valid_value_id: int) -> Optional["ScreeningStatusType"]:
        for item in cls:
            if item.valid_value_id == valid_value_id:
                return item
        return None
