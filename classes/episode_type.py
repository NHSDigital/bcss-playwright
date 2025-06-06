from enum import Enum
from typing import Optional, Dict


class EpisodeType(Enum):
    FOBT = (11350, "FOBT")
    Fobt = (11350, "FOBT Screening")
    BowelScope = (200640, "Bowel Scope")
    Surveillance = (11351, "Surveillance")
    LYNCH_SURVEILLANCE = (305633, "Lynch Surveillance")
    Lynch = (305633, "Lynch")

    def __init__(self, valid_value_id, description):
        self._valid_value_id = valid_value_id
        self._description = description

    @property
    def valid_value_id(self) -> int:
        return self._valid_value_id

    @property
    def description(self) -> str:
        return self._description

    @classmethod
    def by_description(cls, description: str) -> Optional["EpisodeType"]:
        for member in cls:
            if member.description == description:
                return member
        return None

    @classmethod
    def by_description_case_insensitive(
        cls, description: str
    ) -> Optional["EpisodeType"]:
        for member in cls:
            if member.description.lower() == description.lower():
                return member
        return None

    @classmethod
    def by_valid_value_id(cls, valid_value_id: int) -> Optional["EpisodeType"]:
        for member in cls:
            if member.valid_value_id == valid_value_id:
                return member
        return None
