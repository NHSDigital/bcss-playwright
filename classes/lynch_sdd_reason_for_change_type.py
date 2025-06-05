from enum import Enum
from typing import Optional


class LynchSDDReasonForChangeType(Enum):
    CEASED = (305690, "Ceased")
    DATE_OF_BIRTH_AMENDMENT = (306456, "Date of Birth amendment")
    DISCHARGED_PATIENT_UNFIT = (305693, "Discharged, Patient Unfit")
    LYNCH_SURVEILLANCE = (305684, "Lynch Surveillance")
    SELF_REFERRAL = (307130, "Self-referral")
    OPT_IN = (305718, "Opt-in")
    OPT_BACK_INTO_SCREENING_PROGRAMME = (305711, "Opt (Back) into Screening Programme")
    OPT_IN_DUE_TO_ERROR = (305712, "Opt-in due to Error")
    REOPENED_EPISODE = (305706, "Reopened Episode")
    RESULT_REFERRED_FOR_CANCER_TREATMENT = (
        305692,
        "Result referred for Cancer Treatment",
    )
    REVERSAL_OF_DEATH_NOTIFICATION = (305713, "Reversal of Death Notification")
    SELECTED_FOR_LYNCH_SURVEILLANCE = (307071, "Selected for Lynch Surveillance")
    NULL = (None, "null")
    NOT_NULL = (None, "not null")
    UNCHANGED = (None, "unchanged")

    def __init__(self, valid_value_id: Optional[int], description: str):
        self._valid_value_id = valid_value_id
        self._description = description

    @property
    def valid_value_id(self) -> Optional[int]:
        return self._valid_value_id

    @property
    def description(self) -> str:
        return self._description

    @classmethod
    def by_valid_value_id(
        cls, valid_value_id: int
    ) -> Optional["LynchSDDReasonForChangeType"]:
        return next(
            (item for item in cls if item.valid_value_id == valid_value_id), None
        )

    @classmethod
    def by_description(
        cls, description: str
    ) -> Optional["LynchSDDReasonForChangeType"]:
        return next((item for item in cls if item.description == description), None)

    @classmethod
    def by_description_case_insensitive(
        cls, description: str
    ) -> Optional["LynchSDDReasonForChangeType"]:
        return next(
            (item for item in cls if item.description.lower() == description.lower()),
            None,
        )
