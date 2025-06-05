from enum import Enum
from typing import Optional


class GenderType(Enum):
    MALE = (130, 1, "M")
    FEMALE = (131, 2, "F")
    INDETERMINATE = (132, 9, "I")
    NOT_KNOWN = (160, 0, "U")

    def __init__(self, valid_value_id: int, redefined_value: int, allowed_value: str):
        self._valid_value_id = valid_value_id
        self._redefined_value = redefined_value
        self._allowed_value = allowed_value

    @property
    def valid_value_id(self) -> int:
        return self._valid_value_id

    @property
    def redefined_value(self) -> int:
        return self._redefined_value

    @property
    def allowed_value(self) -> str:
        return self._allowed_value

    @classmethod
    def by_valid_value_id(cls, id_: int) -> Optional["GenderType"]:
        return next((item for item in cls if item.valid_value_id == id_), None)

    @classmethod
    def by_redefined_value(cls, redefined_value: int) -> Optional["GenderType"]:
        return next(
            (item for item in cls if item.redefined_value == redefined_value), None
        )
