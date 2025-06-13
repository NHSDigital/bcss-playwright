from enum import Enum
from typing import Optional


class SubjectHasEpisode(Enum):
    YES = "yes"
    NO = "no"

    @classmethod
    def by_description(cls, description: str) -> Optional["SubjectHasEpisode"]:
        for item in cls:
            if item.value == description:
                return item
        return None

    def get_description(self) -> str:
        return self.value
