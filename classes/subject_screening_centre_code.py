from enum import Enum


class SubjectScreeningCentreCode(Enum):
    NONE = "None"
    NULL = "Null"
    NOT_NULL = "Not null"
    USER_SC = "User's SC"
    USER_SCREENING_CENTRE = "User's screening centre"
    USER_ORGANISATION = "User's organisation"

    @property
    def description(self):
        return self.value

    @staticmethod
    def by_description(description: str):
        for item in SubjectScreeningCentreCode:
            if item.description == description:
                return item
        return None  # or raise an exception

    @staticmethod
    def by_description_case_insensitive(description: str):
        description_lower = description.lower()
        for item in SubjectScreeningCentreCode:
            if item.description.lower() == description_lower:
                return item
        return None  # or raise an exception
