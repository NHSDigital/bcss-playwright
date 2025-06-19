class AppointmentSlotType:
    """
    Maps symbolic appointment slot types to their internal IDs.
    Extend as needed.
    """

    _mapping = {
        "clinic": 1001,
        "phone": 1002,
        "video": 1003,
        # Add more mappings here as needed
    }

    @classmethod
    def get_id(cls, description: str) -> int:
        key = description.strip().lower()
        if key not in cls._mapping:
            raise ValueError(f"Unknown appointment slot type: {description}")
        return cls._mapping[key]
