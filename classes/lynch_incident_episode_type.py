class LynchIncidentEpisodeType:
    """
    Maps symbolic values used to filter Lynch incident episode linkage.
    """

    NULL = "null"
    NOT_NULL = "not_null"
    LATEST_EPISODE = "latest_episode"
    EARLIER_EPISODE = "earlier_episode"

    _symbolics = {NULL, NOT_NULL, LATEST_EPISODE, EARLIER_EPISODE}

    @classmethod
    def from_description(cls, description: str) -> str:
        key = description.strip().lower()
        if key not in cls._symbolics:
            raise ValueError(
                f"Unknown Lynch incident episode criteria: '{description}'"
            )
        return key
