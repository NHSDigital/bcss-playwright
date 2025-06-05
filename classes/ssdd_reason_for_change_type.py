from enum import Enum
from typing import Optional


class SSDDReasonForChangeType(Enum):
    CEASED = (67, "Ceased")
    CONTINUE_WITH_SURVEILLANCE = (20285, "Continue with Surveillance")
    DIRECTION_OF_CONSULTANT = (11468, "Direction of Consultant")
    DIRECTION_OF_SCREENING_PRACTITIONER = (
        200278,
        "Direction of Screening Practitioner",
    )
    DISCHARGE_FROM_SURVEILLANCE_AGE = (20039, "Discharge from Surveillance - Age")
    DISCHARGE_FROM_SURVEILLANCE_CANNOT_CONTACT_PATIENT = (
        20042,
        "Discharge from Surveillance - Cannot Contact Patient",
    )
    DISCHARGE_FROM_SURVEILLANCE_CLINICAL_DECISION = (
        20043,
        "Discharge from Surveillance - Clinical Decision",
    )
    DISCHARGE_FROM_SURVEILLANCE_NATIONAL_GUIDELINES = (
        20040,
        "Discharge from Surveillance - National Guidelines",
    )
    DISCHARGE_FROM_SURVEILLANCE_PATIENT_CHOICE = (
        20041,
        "Discharge from Surveillance - Patient Choice",
    )
    DISCHARGE_SURVEILLANCE_REVIEW_2019_GUIDELINES = (
        305549,
        "Discharge, Surveillance Review, 2019 Guidelines",
    )
    DISCHARGED_PATIENT_UNFIT = (20439, "Discharged, Patient Unfit")
    FIT_RESEARCH_PROJECT = (200280, "FIT Research Project")
    MANUAL_AMENDMENT = (20236, "Manual Amendment")
    MANUALLY_REFERRED_TO_SURVEILLANCE_2019_GUIDELINES = (
        305568,
        "Manually Referred to Surveillance, 2019 Guidelines",
    )
    MOVED_TO_LYNCH_SURVEILLANCE = (306451, "Moved to Lynch surveillance")
    PATIENT_REQUEST = (11469, "Patient Request")
    POSTPONE_SURVEILLANCE_REVIEW_2019_GUIDELINES = (
        305550,
        "Postpone, Surveillance Review, 2019 Guidelines",
    )
    REFERRED_FOR_CANCER_TREATMENT = (20304, "Referred for Cancer treatment")
    REINSTATE_SURVEILLANCE = (20266, "Reinstate Surveillance")
    REINSTATE_SURVEILLANCE_DUE_TO_ERROR = (20265, "Reinstate Surveillance due to Error")
    REINSTATE_SURVEILLANCE_FOR_REVERSAL_OF_DEATH_NOTIFICATION = (
        11566,
        "Reinstate Surveillance for Reversal of Death Notification",
    )
    RELATIVE_CARER_REQUEST = (200277, "Relative/Carer Request")
    REOPENED_EPISODE = (20298, "Reopened Episode")
    RESULT_HIGH_RISK_ADENOMA = (11349, "Result - High Risk Adenoma")
    RESULT_INTERMEDIATE_RISK_ADENOMA = (11348, "Result - Intermediate Risk Adenoma")
    RETURNED_UNDELIVERED_MAIL = (200279, "Returned/Undelivered Mail")
    LNPCP = (305614, "Result - LNPCP")
    HIGH_RISK_FINDINGS = (305615, "Result - High-risk findings")

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
    ) -> Optional["SSDDReasonForChangeType"]:
        return next(
            (item for item in cls if item.valid_value_id == valid_value_id), None
        )

    @classmethod
    def by_description(cls, description: str) -> Optional["SSDDReasonForChangeType"]:
        return next((item for item in cls if item.description == description), None)

    @classmethod
    def by_description_case_insensitive(
        cls, description: str
    ) -> Optional["SSDDReasonForChangeType"]:
        return next(
            (item for item in cls if item.description.lower() == description.lower()),
            None,
        )
