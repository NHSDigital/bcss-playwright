class IntendedExtentType:
    """
    Maps intended extent values to nullability flags or valid value IDs.
    """

    NULL = "null"
    NOT_NULL = "not null"

    _label_to_id = {
        "full": 9201,
        "partial": 9202,
        "none": 9203,
        # Add others as needed
    }

    _null_flags = {NULL, NOT_NULL}

    @classmethod
    def from_description(cls, description: str):
        key = description.strip().lower()
        if key in cls._null_flags:
            return key
        if key in cls._label_to_id:
            return cls._label_to_id[key]
        raise ValueError(f"Unknown intended extent: '{description}'")

    @classmethod
    def get_id(cls, description: str) -> int:
        key = description.strip().lower()
        if key not in cls._label_to_id:
            raise ValueError(f"No ID available for intended extent: '{description}'")
        return cls._label_to_id[key]

    @classmethod
    def get_description(cls, sentinel: str) -> str:
        if sentinel == cls.NULL:
            return "NULL"
        if sentinel == cls.NOT_NULL:
            return "NOT NULL"
        raise ValueError(f"Invalid sentinel: '{sentinel}'")
