class SurveillanceReviewCaseType:
    """
    Maps surveillance review case type labels to valid value IDs.
    """

    _label_to_id = {
        "routine": 9401,
        "escalation": 9402,
        "clinical discussion": 9403,
        # Extend with additional mappings as needed
    }

    @classmethod
    def get_id(cls, description: str) -> int:
        key = description.strip().lower()
        if key not in cls._label_to_id:
            raise ValueError(f"Unknown review case type: '{description}'")
        return cls._label_to_id[key]
