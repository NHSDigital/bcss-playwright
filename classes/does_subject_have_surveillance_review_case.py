class DoesSubjectHaveSurveillanceReviewCase:
    """
    Maps binary criteria for presence of a surveillance review case.
    """

    YES = "yes"
    NO = "no"

    _valid_values = {YES, NO}

    @classmethod
    def from_description(cls, description: str) -> str:
        key = description.strip().lower()
        if key not in cls._valid_values:
            raise ValueError(
                f"Unknown surveillance review case presence: '{description}'"
            )
        return key
