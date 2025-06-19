class HasDateOfDeathRemoval:
    """
    Maps binary filter for presence of date-of-death removal record.
    """

    YES = "yes"
    NO = "no"

    _valid_values = {YES, NO}

    @classmethod
    def from_description(cls, description: str) -> str:
        key = description.strip().lower()
        if key not in cls._valid_values:
            raise ValueError(
                f"Invalid value for date-of-death removal filter: '{description}'"
            )
        return key
