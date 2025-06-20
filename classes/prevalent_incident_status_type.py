class PrevalentIncidentStatusType:
    """
    Maps symbolic values for FOBT prevalent/incident episode classification.
    """

    PREVALENT = "prevalent"
    INCIDENT = "incident"

    _valid_values = {PREVALENT, INCIDENT}

    @classmethod
    def from_description(cls, description: str) -> str:
        key = description.strip().lower()
        if key not in cls._valid_values:
            raise ValueError(f"Unknown FOBT episode status: '{description}'")
        return key
