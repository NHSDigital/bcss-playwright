from typing import Optional, Dict


class EpisodeResultType:
    NO_RESULT = (20311, "No Result")
    NORMAL = (20312, "Normal (No Abnormalities Found)")
    LOW_RISK_ADENOMA = (20314, "Low-risk Adenoma")
    INTERMEDIATE_RISK_ADENOMA = (20315, "Intermediate-risk Adenoma")
    HIGH_RISK_ADENOMA = (20316, "High-risk Adenoma")
    CANCER_DETECTED = (20317, "Cancer Detected")
    ABNORMAL = (20313, "Abnormal")
    CANCER_NOT_CONFIRMED = (305001, "Cancer not confirmed")
    HIGH_RISK_FINDINGS = (305606, "High-risk findings")
    LNPCP = (305607, "LNPCP")
    BOWEL_SCOPE_NON_PARTICIPATION = (605002, "Bowel scope non-participation")
    FOBT_INADEQUATE_PARTICIPATION = (605003, "FOBt inadequate participation")
    DEFINITIVE_NORMAL_FOBT_OUTCOME = (605005, "Definitive normal FOBt outcome")
    DEFINITIVE_ABNORMAL_FOBT_OUTCOME = (605006, "Definitive abnormal FOBt outcome")
    HIGH_RISK_FINDINGS_SURVEILLANCE_NON_PARTICIPATION = (
        305619,
        "High-risk findings Surveillance non-participation",
    )
    LNPCP_SURVEILLANCE_NON_PARTICIPATION = (
        305618,
        "LNPCP Surveillance non-participation",
    )
    HIGH_RISK_SURVEILLANCE_NON_PARTICIPATION = (
        605004,
        "High-risk Surveillance non-participation",
    )
    INTERMEDIATE_RISK_SURVEILLANCE_NON_PARTICIPATION = (
        605007,
        "Intermediate-risk Surveillance non-participation",
    )
    LYNCH_NON_PARTICIPATION = (305688, "Lynch non-participation")
    ANY_SURVEILLANCE_NON_PARTICIPATION = (0, "(Any) Surveillance non-participation")
    NULL = (0, "Null")
    NOT_NULL = (0, "Not Null")

    _all_types = [
        NO_RESULT,
        NORMAL,
        LOW_RISK_ADENOMA,
        INTERMEDIATE_RISK_ADENOMA,
        HIGH_RISK_ADENOMA,
        CANCER_DETECTED,
        ABNORMAL,
        CANCER_NOT_CONFIRMED,
        HIGH_RISK_FINDINGS,
        LNPCP,
        BOWEL_SCOPE_NON_PARTICIPATION,
        FOBT_INADEQUATE_PARTICIPATION,
        DEFINITIVE_NORMAL_FOBT_OUTCOME,
        DEFINITIVE_ABNORMAL_FOBT_OUTCOME,
        HIGH_RISK_FINDINGS_SURVEILLANCE_NON_PARTICIPATION,
        LNPCP_SURVEILLANCE_NON_PARTICIPATION,
        HIGH_RISK_SURVEILLANCE_NON_PARTICIPATION,
        INTERMEDIATE_RISK_SURVEILLANCE_NON_PARTICIPATION,
        LYNCH_NON_PARTICIPATION,
        ANY_SURVEILLANCE_NON_PARTICIPATION,
        NULL,
        NOT_NULL,
    ]

    _descriptions: Dict[str, "EpisodeResultType"] = {}
    _lowercase_descriptions: Dict[str, "EpisodeResultType"] = {}
    _valid_value_ids: Dict[int, "EpisodeResultType"] = {}

    def __init__(self, valid_value_id: int, description: str):
        self.valid_value_id = valid_value_id
        self.description = description

    @classmethod
    def _init_types(cls):
        if not cls._descriptions:
            for valid_value_id, description in cls._all_types:
                instance = cls(valid_value_id, description)
                cls._descriptions[description] = instance
                cls._lowercase_descriptions[description.lower()] = instance
                # Only map the first occurrence of each valid_value_id
                if valid_value_id not in cls._valid_value_ids:
                    cls._valid_value_ids[valid_value_id] = instance

    @classmethod
    def by_description(cls, description: str) -> Optional["EpisodeResultType"]:
        cls._init_types()
        return cls._descriptions.get(description)

    @classmethod
    def by_description_case_insensitive(
        cls, description: str
    ) -> Optional["EpisodeResultType"]:
        cls._init_types()
        return cls._lowercase_descriptions.get(description.lower())

    @classmethod
    def by_valid_value_id(cls, valid_value_id: int) -> Optional["EpisodeResultType"]:
        cls._init_types()
        return cls._valid_value_ids.get(valid_value_id)

    def get_id(self) -> int:
        return self.valid_value_id

    def get_description(self) -> str:
        return self.description

    def __eq__(self, other):
        if isinstance(other, EpisodeResultType):
            return (
                self.valid_value_id == other.valid_value_id
                and self.description == other.description
            )
        return False

    def __repr__(self):
        return f"EpisodeResultType({self.valid_value_id}, '{self.description}')"
