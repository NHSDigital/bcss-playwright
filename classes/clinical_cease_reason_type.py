from enum import Enum
from typing import Optional, Dict


class ClinicalCeaseReasonType(Enum):
    # BCSS values
    ALREADY_INVOLVED_IN_SURVEILLANCE_PROGRAMME_OUTSIDE_BCSP = (
        11369,
        "Already involved in Surveillance Programme outside BCSP",
    )
    CLINICAL_ASSESSMENT_INDICATES_CEASE_SURVEILLANCE_AND_SCREENING = (
        20066,
        "Clinical Assessment indicates Cease Surveillance and Screening",
    )
    CURRENTLY_UNDER_TREATMENT = (11371, "Currently under treatment")
    NO_FUNCTIONING_COLON = (11366, "No functioning colon")
    RECENT_COLONOSCOPY = (11372, "Recent colonoscopy")
    REFER_TO_SYMPTOMATIC_SERVICE = (205274, "Refer to Symptomatic Service")
    TERMINAL_ILLNESS = (11367, "Terminal Illness")
    UNDER_TREATMENT_FOR_ULCERATIVE_COLITIS_CROHNS_DISEASE_BOWEL_CANCER_OR_OTHER_RESULTING_IN_CEASE = (
        11368,
        "Under treatment for ulcerative colitis, Crohn's disease, bowel cancer or other, resulting in cease",
    )
    UNFIT_FOR_FURTHER_INVESTIGATION = (11373, "Unfit for further investigation")

    # Extra subject selection criteria values
    NULL = (None, "Null")
    NOT_NULL = (None, "Not Null")

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
    def _build_lookup_maps(cls):
        cls._descriptions: Dict[str, "ClinicalCeaseReasonType"] = {}
        cls._lowercase_descriptions: Dict[str, "ClinicalCeaseReasonType"] = {}
        cls._valid_value_ids: Dict[int, "ClinicalCeaseReasonType"] = {}

        for member in cls:
            if member.description:
                cls._descriptions[member.description] = member
                cls._lowercase_descriptions[member.description.lower()] = member
            if member.valid_value_id is not None:
                cls._valid_value_ids[member.valid_value_id] = member

    @classmethod
    def by_description(cls, description: str) -> Optional["ClinicalCeaseReasonType"]:
        if not hasattr(cls, "_descriptions"):
            cls._build_lookup_maps()
        return cls._descriptions.get(description)

    @classmethod
    def by_description_case_insensitive(
        cls, description: str
    ) -> Optional["ClinicalCeaseReasonType"]:
        if not hasattr(cls, "_lowercase_descriptions"):
            cls._build_lookup_maps()
        return cls._lowercase_descriptions.get(description.lower())

    @classmethod
    def by_valid_value_id(
        cls, valid_value_id: int
    ) -> Optional["ClinicalCeaseReasonType"]:
        if not hasattr(cls, "_valid_value_ids"):
            cls._build_lookup_maps()
        return cls._valid_value_ids.get(valid_value_id)
