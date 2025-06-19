class SurveillanceReviewStatusType:
    """
    Maps review status labels to valid value IDs used in surveillance review filtering.
    """

    _label_to_id = {
        "awaiting review": 9301,
        "in progress": 9302,
        "completed": 9303,
        # Extend if needed
    }

    @classmethod
    def get_id(cls, description: str) -> int:
        key = description.strip().lower()
        if key not in cls._label_to_id:
            raise ValueError(f"Unknown surveillance review status: '{description}'")
        return cls._label_to_id[key]
