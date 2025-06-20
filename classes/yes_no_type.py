class YesNoType:
    YES = "yes"
    NO = "no"

    _valid = {YES, NO}

    @classmethod
    def from_description(cls, description: str) -> str:
        key = description.strip().lower()
        if key not in cls._valid:
            raise ValueError(f"Expected 'yes' or 'no', got: '{description}'")
        return key
