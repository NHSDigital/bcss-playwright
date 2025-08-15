from enum import Enum
from typing import Optional, Dict


class DiagnosticTestType(Enum):
    """
    Enum representing diagnostic test types, with valid value IDs, descriptions, categories, and allowed status.
    """

    BARIUM_ENEMA = (16003, "Barium Enema", "RADIOLOGY", "DISALLOWED")
    CT_COLONOGRAPHY = (16087, "CT Colonography", "RADIOLOGY", "ALLOWED")
    COLONOSCOPY = (16002, "Colonoscopy", "COLONOSCOPY", "ALLOWED")
    FLEXIBLE_SIGMOIDOSCOPY = (16004, "Flexible Sigmoidoscopy", "COLONOSCOPY", "ALLOWED")
    LIMITED_COLONOSCOPY = (17996, "Limited Colonoscopy", "COLONOSCOPY", "ALLOWED")
    NHS_BOWEL_SCOPE = (200554, "NHS bowel scope", "COLONOSCOPY", "ALLOWED")
    SCAN_XRAY = (16005, "Scan (x-ray)", "RADIOLOGY", "DISALLOWED")
    STANDARD_ABDOMINO_PELVIC_CT_SCAN = (
        16088,
        "Standard Abdomino-pelvic CT Scan",
        "RADIOLOGY",
        "DISALLOWED",
    )
    ANY = (0, "Any", "", "")

    def __init__(
        self, valid_value_id: int, description: str, category: str, allowed: str
    ):
        self._valid_value_id: int = valid_value_id
        self._description: str = description
        self._category: str = category
        self._allowed: str = allowed

    @property
    def valid_value_id(self) -> int:
        """Returns the valid value ID for the diagnostic test type."""
        return self._valid_value_id

    @property
    def description(self) -> str:
        """Returns the description for the diagnostic test type."""
        return self._description

    @property
    def category(self) -> str:
        """Returns the category for the diagnostic test type."""
        return self._category

    @property
    def allowed(self) -> str:
        """Returns the allowed status for the diagnostic test type."""
        return self._allowed

    @classmethod
    def _build_maps(cls) -> None:
        if not hasattr(cls, "_descriptions"):
            cls._descriptions: Dict[str, DiagnosticTestType] = {}
            cls._lowercase_descriptions: Dict[str, DiagnosticTestType] = {}
            cls._valid_value_ids: Dict[int, DiagnosticTestType] = {}
            for item in cls:
                cls._descriptions[item.description] = item
                cls._lowercase_descriptions[item.description.lower()] = item
                cls._valid_value_ids[item.valid_value_id] = item

    @classmethod
    def by_description(cls, description: str) -> Optional["DiagnosticTestType"]:
        """
        Returns the DiagnosticTestType matching the given description.
        """
        cls._build_maps()
        return cls._descriptions.get(description)

    @classmethod
    def by_description_case_insensitive(
        cls, description: str
    ) -> Optional["DiagnosticTestType"]:
        """
        Returns the DiagnosticTestType matching the given description (case-insensitive).
        """
        cls._build_maps()
        return cls._lowercase_descriptions.get(description.lower())

    @classmethod
    def by_valid_value_id(cls, valid_value_id: int) -> Optional["DiagnosticTestType"]:
        """
        Returns the DiagnosticTestType matching the given valid value ID.
        """
        cls._build_maps()
        return cls._valid_value_ids.get(valid_value_id)

    def get_valid_value_id(self) -> int:
        """Returns the valid value ID for the diagnostic test type."""
        return self._valid_value_id

    def get_description(self) -> str:
        """Returns the description for the diagnostic test type."""
        return self._description

    def get_category(self) -> str:
        """Returns the category for the diagnostic test type."""
        return self._category

    def get_allowed(self) -> str:
        """Returns the allowed status for the diagnostic test type."""
        return self._allowed
