from enum import Enum
from typing import Optional, Dict


class BowelScopeDDReasonForChangeType(Enum):
    Ceased = (200669, "Ceased")
    DateOfBirthAmendment = (205266, "Date of birth amendment")
    EligibleToBeInvitedForFsScreening = (
        200685,
        "Eligible to be invited for FS Screening",
    )
    FsScreeningEpisodeOpened = (205002, "FS Screening episode opened")
    MultipleDateOfBirthChanges = (202426, "Multiple Date of Birth Changes")
    NoLongerEligibleToBeInvitedForFsScreening = (
        200668,
        "No longer eligible to be invited for FS Screening",
    )
    ReopenedFsEpisode = (205012, "Reopened FS Episode")
    SeekingFurtherData = (200670, "Seeking further data")

    def __init__(self, valid_value_id: int, description: str):
        self._valid_value_id: int = valid_value_id
        self._description: str = description

    @property
    def valid_value_id(self) -> int:
        return self._valid_value_id

    @property
    def description(self) -> str:
        return self._description

    @classmethod
    def _descriptions(cls) -> Dict[str, "BowelScopeDDReasonForChangeType"]:
        return {item.description: item for item in cls}

    @classmethod
    def _lowercase_descriptions(cls) -> Dict[str, "BowelScopeDDReasonForChangeType"]:
        return {item.description.lower(): item for item in cls}

    @classmethod
    def _valid_value_ids(cls) -> Dict[int, "BowelScopeDDReasonForChangeType"]:
        return {item.valid_value_id: item for item in cls}

    @classmethod
    def by_description(
        cls, description: Optional[str]
    ) -> Optional["BowelScopeDDReasonForChangeType"]:
        if description is None:
            return None
        return cls._lowercase_descriptions().get(description.lower())

    @classmethod
    def by_valid_value_id(
        cls, valid_value_id: int
    ) -> Optional["BowelScopeDDReasonForChangeType"]:
        return cls._valid_value_ids().get(valid_value_id)
