class LatestEpisodeLatestInvestigationDataset:
    """
    Maps descriptive investigation filter criteria to internal constants.
    Used to drive investigation dataset filtering in latest episode.
    """

    NONE = "none"
    COLONOSCOPY_NEW = "colonoscopy_new"
    LIMITED_COLONOSCOPY_NEW = "limited_colonoscopy_new"
    FLEXIBLE_SIGMOIDOSCOPY_NEW = "flexible_sigmoidoscopy_new"
    CT_COLONOGRAPHY_NEW = "ct_colonography_new"
    ENDOSCOPY_INCOMPLETE = "endoscopy_incomplete"
    RADIOLOGY_INCOMPLETE = "radiology_incomplete"

    _valid_values = {
        NONE,
        COLONOSCOPY_NEW,
        LIMITED_COLONOSCOPY_NEW,
        FLEXIBLE_SIGMOIDOSCOPY_NEW,
        CT_COLONOGRAPHY_NEW,
        ENDOSCOPY_INCOMPLETE,
        RADIOLOGY_INCOMPLETE,
    }

    @classmethod
    def from_description(cls, description: str) -> str:
        key = description.strip().lower()
        if key not in cls._valid_values:
            raise ValueError(f"Unknown investigation dataset filter: '{description}'")
        return key
