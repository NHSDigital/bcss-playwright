from enum import Enum
from typing import Optional


class AddressContactType(Enum):
    WORK = (13056, "WORK")
    HOME = (13057, "HOME")

    def __init__(self, valid_value_id: int, allowed_value: str):
        self._valid_value_id = valid_value_id
        self._allowed_value = allowed_value

    @property
    def valid_value_id(self) -> int:
        return self._valid_value_id

    @property
    def allowed_value(self) -> str:
        return self._allowed_value

    @classmethod
    def by_valid_value_id(
        cls, address_contact_type_id: int
    ) -> Optional["AddressContactType"]:
        return next(
            (item for item in cls if item.valid_value_id == address_contact_type_id),
            None,
        )
