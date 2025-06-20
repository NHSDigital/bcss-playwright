class NotifyEventStatus:
    _label_to_id = {
        "S1": 9901,
        "S2": 9902,
        "M1": 9903,
        # Extend as needed
    }

    @classmethod
    def get_id(cls, description: str) -> int:
        key = description.strip().upper()
        if key not in cls._label_to_id:
            raise ValueError(f"Unknown Notify event type: '{description}'")
        return cls._label_to_id[key]
