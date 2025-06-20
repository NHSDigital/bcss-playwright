class LynchDueDateReasonType:
    """
    Maps Lynch surveillance due date reason descriptions to IDs and symbolic types.
    """

    NULL = "null"
    NOT_NULL = "not_null"
    UNCHANGED = "unchanged"

    _label_to_id = {
        "holiday": 9801,
        "clinical request": 9802,
        "external delay": 9803,
        # Extend as needed
    }

    @classmethod
    def from_description(cls, description: str):
        key = description.strip().lower()
        if key in {cls.NULL, cls.NOT_NULL, cls.UNCHANGED}:
            return key
        if key in cls._label_to_id:
            return cls._label_to_id[key]
        raise ValueError(f"Unknown Lynch due date change reason: '{description}'")
