class LatestEpisodeHasDataset:
    """
    Interprets presence and completion status of datasets in the latest episode.
    """

    NO = "no"
    YES_INCOMPLETE = "yes_incomplete"
    YES_COMPLETE = "yes_complete"
    PAST = "past"

    _valid_values = {NO, YES_INCOMPLETE, YES_COMPLETE, PAST}

    @classmethod
    def from_description(cls, description: str) -> str:
        key = description.strip().lower()
        if key not in cls._valid_values:
            raise ValueError(f"Unknown dataset status: '{description}'")
        return key
