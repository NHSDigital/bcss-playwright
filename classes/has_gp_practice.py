from enum import Enum


class HasGPPractice(Enum):
    NO = "no"
    YES_ACTIVE = "yes - active"
    YES_INACTIVE = "yes - inactive"

    @classmethod
    def by_description(cls, description: str):
        for member in cls:
            if member.value == description:
                return member
        return None

    def get_description(self):
        return self.value
