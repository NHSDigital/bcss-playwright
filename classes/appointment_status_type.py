class AppointmentStatusType:
    """
    Maps descriptive appointment statuses to internal IDs.
    Extend with real values as needed.
    """

    _mapping = {
        "booked": 2001,
        "attended": 2002,
        "cancelled": 2003,
        "dna": 2004,  # Did Not Attend
    }

    @classmethod
    def get_id(cls, description: str) -> int:
        key = description.strip().lower()
        if key not in cls._mapping:
            raise ValueError(f"Unknown appointment status: {description}")
        return cls._mapping[key]
