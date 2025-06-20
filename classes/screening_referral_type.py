class ScreeningReferralType:
    """
    Maps screening referral descriptions to valid value IDs.
    """

    _label_to_id = {
        "gp": 9701,
        "self referral": 9702,
        "hospital": 9703,
        # Add more as needed
    }

    @classmethod
    def get_id(cls, description: str) -> int:
        key = description.strip().lower()
        if key not in cls._label_to_id:
            raise ValueError(f"Unknown screening referral type: '{description}'")
        return cls._label_to_id[key]
