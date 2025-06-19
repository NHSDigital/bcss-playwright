class EpisodeResultType:
    """
    Maps description labels to episode result types and valid value IDs.
    """

    NULL = "null"
    NOT_NULL = "not_null"
    ANY_SURVEILLANCE_NON_PARTICIPATION = "any_surveillance_non_participation"

    _label_to_id = {
        "normal": 9501,
        "abnormal": 9502,
        "surveillance offered": 9503,
        # Add real mappings as needed
    }

    @classmethod
    def from_description(cls, description: str):
        key = description.strip().lower()
        if key in {cls.NULL, cls.NOT_NULL, cls.ANY_SURVEILLANCE_NON_PARTICIPATION}:
            return key
        if key in cls._label_to_id:
            return cls._label_to_id[key]
        raise ValueError(f"Unknown episode result type: '{description}'")
