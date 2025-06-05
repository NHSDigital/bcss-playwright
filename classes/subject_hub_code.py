from enum import Enum
from typing import Dict, Optional


class SubjectHubCode(Enum):
    USER_HUB = "user's hub"
    USER_ORGANISATION = "user's organisation"

    @property
    def description(self) -> str:
        return self.value

    @classmethod
    def by_description(cls, description: str) -> Optional["SubjectHubCode"]:
        # Build reverse lookup map once and store it as a class attribute
        if not hasattr(cls, "_description_map"):
            cls._description_map: Dict[str, SubjectHubCode] = {
                member.value: member for member in cls
            }
        return cls._description_map.get(description)
