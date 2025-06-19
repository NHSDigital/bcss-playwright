class DiagnosticTestHasOutcomeOfResult:
    """
    Maps outcome-of-result descriptions to logical flags or valid value IDs.
    """

    YES = "yes"
    NO = "no"

    _label_to_id = {
        "referred": 9101,
        "treated": 9102,
        "not required": 9103,
        # Extend as needed
    }

    _valid_flags = {YES, NO}

    @classmethod
    def from_description(cls, description: str):
        key = description.strip().lower()
        if key in cls._valid_flags:
            return key
        if key in cls._label_to_id:
            return cls._label_to_id[key]
        raise ValueError(f"Unknown outcome-of-result description: '{description}'")

    @classmethod
    def get_id(cls, description: str) -> int:
        key = description.strip().lower()
        if key not in cls._label_to_id:
            raise ValueError(f"No ID available for outcome: '{description}'")
        return cls._label_to_id[key]
