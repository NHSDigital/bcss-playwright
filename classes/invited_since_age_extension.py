class InvitedSinceAgeExtension:
    """
    Maps subject invitation criteria based on age extension presence.
    """

    YES = "yes"
    NO = "no"

    _valid_values = {YES, NO}

    @classmethod
    def from_description(cls, description: str) -> str:
        key = description.strip().lower()
        if key not in cls._valid_values:
            raise ValueError(
                f"Invalid invited-since-age-extension flag: '{description}'"
            )
        return key
