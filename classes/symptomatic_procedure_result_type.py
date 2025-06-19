class SymptomaticProcedureResultType:
    """
    Maps symptomatic surgery result labels to valid value IDs.
    """

    _label_to_id = {
        "normal": 9601,
        "inconclusive": 9602,
        "cancer detected": 9603,
        # Add more as needed
    }

    @classmethod
    def get_id(cls, description: str) -> int:
        key = description.strip().lower()
        if key not in cls._label_to_id:
            raise ValueError(f"Unknown symptomatic procedure result: '{description}'")
        return cls._label_to_id[key]
