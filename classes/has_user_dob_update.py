from enum import Enum
from typing import Optional, Dict


class HasUserDobUpdate(Enum):
    NO = "no"
    YES = "yes"

    @classmethod
    def by_description(cls, description: str) -> Optional["HasUserDobUpdate"]:
        for item in cls:
            if item.value == description:
                return item
        return None

    def get_description(self) -> str:
        return self.value
