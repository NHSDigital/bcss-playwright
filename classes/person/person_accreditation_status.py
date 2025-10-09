from enum import Enum
from typing import Optional


class PersonAccreditationStatus(Enum):
    """
    Enum representing a person's accreditation status, with utility methods for lookup by description.
    """

    ACCREDITED_AT_SUBJECTS_LATEST_DIAGNOSTIC_TEST = (
        "Accredited at subject's latest diagnostic test"
    )
    CURRENT = "Current"
    EXPIRED = "Expired"
    EXPIRES_SOON = "Expiring soon"
    NONE = "None"
    NOT_ACCREDITED_AT_SUBJECTS_LATEST_DIAGNOSTIC_TEST = (
        "Not accredited at subject's latest diagnostic test"
    )

    @property
    def description(self) -> str:
        """
        Returns the description for the accreditation status.
        """
        return self.value

    @classmethod
    def by_description(cls, description: str) -> Optional["PersonAccreditationStatus"]:
        """
        Returns the enum member matching the given description (case-sensitive).
        """
        for member in cls:
            if member.description == description:
                return member
        return None

    @classmethod
    def by_description_case_insensitive(
        cls, description: str
    ) -> Optional["PersonAccreditationStatus"]:
        """
        Returns the enum member matching the given description (case-insensitive).
        """
        desc_lower = description.lower()
        for member in cls:
            if member.description.lower() == desc_lower:
                return member
        return None

    def get_description(self) -> str:
        """
        Returns the description.
        """
        return self.description
