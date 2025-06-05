from enum import Enum
from typing import Optional


class AddressType(Enum):
    MAIN_REGISTERED_ADDRESS = (13042, "H")
    TEMPORARY_ADDRESS = (13043, "T")

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
    def by_valid_value_id(cls, address_type_id: int) -> Optional["AddressType"]:
        return next(
            (item for item in cls if item.valid_value_id == address_type_id), None
        )
