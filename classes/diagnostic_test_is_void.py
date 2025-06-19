class DiagnosticTestIsVoid:
    """
    Maps descriptive yes/no flags to test void state checks.
    """

    YES = "yes"
    NO = "no"

    _valid_values = {YES, NO}

    @classmethod
    def from_description(cls, description: str) -> str:
        key = description.strip().lower()
        if key not in cls._valid_values:
            raise ValueError(f"Unknown test void flag: '{description}'")
        return key
