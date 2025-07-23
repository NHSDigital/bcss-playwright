from enum import Enum
from typing import Optional, Dict


class EpisodeStatusType(Enum):
    """
    Enum representing episode status types with valid value IDs and descriptions.
    """

    Closed = (11353, "Closed")
    Open = (11352, "Open")
    Paused = (11354, "Paused")
    Pending = (11354, "Pending")

    def __init__(self, valid_value_id: int, description: str):
        self._valid_value_id: int = valid_value_id
        self._description: str = description

    @property
    def valid_value_id(self) -> int:
        """Returns the valid value ID for the episode status."""
        return self._valid_value_id

    @property
    def description(self) -> str:
        """Returns the description for the episode status."""
        return self._description

    @classmethod
    def _build_maps(cls) -> None:
        if not hasattr(cls, "_descriptions"):
            cls._descriptions: Dict[str, EpisodeStatusType] = {}
            cls._lowercase_descriptions: Dict[str, EpisodeStatusType] = {}
            cls._valid_value_ids: Dict[int, EpisodeStatusType] = {}
            for item in cls:
                cls._descriptions[item.description] = item
                cls._lowercase_descriptions[item.description.lower()] = item
                cls._valid_value_ids[item.valid_value_id] = item

    @classmethod
    def by_description(cls, description: str) -> Optional["EpisodeStatusType"]:
        """
        Returns the EpisodeStatusType matching the given description.
        """
        cls._build_maps()
        return cls._descriptions.get(description)

    @classmethod
    def by_description_case_insensitive(
        cls, description: str
    ) -> Optional["EpisodeStatusType"]:
        """
        Returns the EpisodeStatusType matching the given description (case-insensitive).
        """
        cls._build_maps()
        return cls._lowercase_descriptions.get(description.lower())

    @classmethod
    def by_valid_value_id(cls, valid_value_id: int) -> Optional["EpisodeStatusType"]:
        """
        Returns the EpisodeStatusType matching the given valid value ID.
        """
        cls._build_maps()
        return cls._valid_value_ids.get(valid_value_id)

    def get_id(self) -> int:
        """
        Returns the valid value ID for the episode status.
        """
        return self._valid_value_id

    def get_description(self) -> str:
        """
        Returns the description for the
        """
        return self._description
