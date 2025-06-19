class DiagnosticTestType:
    """
    Maps descriptive diagnostic test types to valid value IDs.
    Extend or replace these with values pulled from the actual codebook or database.
    """

    _mapping = {
        "pcr": 3001,
        "antigen": 3002,
        "lateral flow": 3003,
        # Add more mappings as needed
    }

    @classmethod
    def get_valid_value_id(cls, description: str) -> int:
        key = description.strip().lower()
        if key not in cls._mapping:
            raise ValueError(f"Unknown diagnostic test type: '{description}'")
        return cls._mapping[key]
