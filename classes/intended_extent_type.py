from enum import Enum
from typing import Optional, Dict


class IntendedExtentType(Enum):
    """
    Enum representing intended extent locations for investigation datasets,
    with valid value IDs and descriptions.
    """

    ANASTOMOSIS = (17241, "Anastomosis")
    ANUS = (17231, "Anus")
    APPENDIX = (17242, "Appendix")
    ASCENDING_COLON = (17238, "Ascending Colon")
    CAECUM = (17239, "Caecum")
    DESCENDING_COLON = (17234, "Descending Colon")
    DISTAL_SIGMOID = (17965, "Distal sigmoid")  # Legacy value
    ENTIRE_COLON = (17245, "Entire colon")  # Legacy value
    HEPATIC_FLEXURE = (17237, "Hepatic Flexure")
    ILEUM = (17240, "Ileum")
    LEFT_COLON = (17244, "Left colon")  # Legacy value
    MID_SIGMOID = (17966, "Mid sigmoid")  # Legacy value
    PROXIMAL_SIGMOID = (17967, "Proximal sigmoid")  # Legacy value
    RECTO_SIGMOID = (17243, "Recto/Sigmoid")  # Legacy value
    RECTOSIGMOID_JUNCTION = (17964, "Rectosigmoid junction")  # Legacy value
    RECTUM = (17232, "Rectum")
    SIGMOID_COLON = (17233, "Sigmoid Colon")
    SPLENIC_FLEXURE = (17235, "Splenic Flexure")
    TRANSVERSE_COLON = (17236, "Transverse Colon")
    NULL = (None, "NULL")
    NOT_NULL = (None, "NOT NULL")

    def __init__(self, valid_value_id: Optional[int], description: str):
        self._valid_value_id: Optional[int] = valid_value_id
        self._description: str = description

    @property
    def valid_value_id(self) -> Optional[int]:
        """Returns the valid value ID for the intended extent type."""
        return self._valid_value_id

    @property
    def description(self) -> str:
        """Returns the description for the intended extent type."""
        return self._description

    @classmethod
    def _build_maps(cls) -> None:
        if not hasattr(cls, "_descriptions"):
            cls._descriptions: Dict[str, IntendedExtentType] = {}
            cls._lowercase_descriptions: Dict[str, IntendedExtentType] = {}
            cls._valid_value_ids: Dict[Optional[int], IntendedExtentType] = {}
            for item in cls:
                cls._descriptions[item.description] = item
                cls._lowercase_descriptions[item.description.lower()] = item
                cls._valid_value_ids[item.valid_value_id] = item

    @classmethod
    def by_description(cls, description: str) -> Optional["IntendedExtentType"]:
        """
        Returns the IntendedExtentType matching the given description.
        """
        cls._build_maps()
        return cls._descriptions.get(description)

    @classmethod
    def by_description_case_insensitive(
        cls, description: str
    ) -> Optional["IntendedExtentType"]:
        """
        Returns the IntendedExtentType matching the given description (case-insensitive).
        """
        cls._build_maps()
        return cls._lowercase_descriptions.get(description.lower())

    @classmethod
    def by_valid_value_id(
        cls, valid_value_id: Optional[int]
    ) -> Optional["IntendedExtentType"]:
        """
        Returns the IntendedExtentType matching the given valid value ID.
        """
        cls._build_maps()
        return cls._valid_value_ids.get(valid_value_id)

    def get_id(self) -> Optional[int]:
        """Returns the valid value ID for the intended extent type."""
        return self._valid_value_id

    def get_description(self) -> str:
        """Returns the description for the intended extent type."""
        return self._description
