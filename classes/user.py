from typing import Optional
from classes.organisation import Organisation


class User:
    def __init__(
        self,
        user_id: Optional[int] = None,
        role_id: Optional[int] = None,
        pio_id: Optional[int] = None,
        organisation: Optional[Organisation] = None,
    ):
        self._user_id = user_id
        self._role_id = role_id
        self._pio_id = pio_id
        self._organisation = organisation

    @property
    def user_id(self) -> Optional[int]:
        return self._user_id

    @user_id.setter
    def user_id(self, value: int) -> None:
        self._user_id = value

    @property
    def role_id(self) -> Optional[int]:
        return self._role_id

    @role_id.setter
    def role_id(self, value: int) -> None:
        self._role_id = value

    @property
    def pio_id(self) -> Optional[int]:
        return self._pio_id

    @pio_id.setter
    def pio_id(self, value: int) -> None:
        self._pio_id = value

    @property
    def organisation(self) -> Optional[Organisation]:
        return self._organisation

    @organisation.setter
    def organisation(self, value: Organisation) -> None:
        self._organisation = value

    def __str__(self) -> str:
        org_id = (
            self.organisation.get_organisation_id() if self.organisation else "None"
        )
        return f"User [userId={self.user_id}, orgId={org_id}, roleId={self.role_id}]"
