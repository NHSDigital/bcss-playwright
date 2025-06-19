class DiagnosticTestHasResult:
    """
    Maps descriptive flags and result labels to internal identifiers.
    Used for interpreting criteria values for diagnostic test result presence or type.
    """

    YES = "yes"
    NO = "no"

    _label_to_id = {
        "positive": 9001,
        "negative": 9002,
        "indeterminate": 9003,
        # Add additional mappings as needed
    }

    _valid_flags = {YES, NO}

    @classmethod
    def from_description(cls, description: str):
        key = description.strip().lower()
        if key in cls._valid_flags:
            return key
        if key in cls._label_to_id:
            return cls._label_to_id[key]
        raise ValueError(f"Unknown diagnostic test result description: '{description}'")

    @classmethod
    def get_id(cls, description: str) -> int:
        key = description.strip().lower()
        if key not in cls._label_to_id:
            raise ValueError(f"No ID available for result description: '{description}'")
        return cls._label_to_id[key]
